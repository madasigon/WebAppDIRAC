from WebAppDIRAC.Lib.WebHandler import WebHandler, asyncGen
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.Core.DISET.TransferClient import TransferClient
from DIRAC.Core.Utilities import Time, DEncode
from DIRAC import gConfig
import tempfile
import json
import tornado

class ActivityMonitorHandler( WebHandler ):

  AUTH_PROPS = "authenticated"

  @asyncGen
  def web_getActivityData( self ):
    try:
      start = int( self.request.arguments[ 'start' ][0] )
    except:
      start = 0
    try:
      limit = int( self.request.arguments[ 'limit' ][0] )
    except:
      limit = 0

    try:
      sortField = str( self.request.arguments[ 'sortField' ][0] ).replace( "_", "." )
      sortDir = str( self.request.arguments[ 'sortDirection' ][0] )
      sort = [ ( sortField, sortDir ) ]
    except:
      sort = []

    rpcClient = RPCClient( "Framework/Monitoring" )
    retVal = yield self.threadTask( rpcClient.getActivitiesContents, {}, sort, start, limit )

    if not retVal[ 'OK' ]:
      self.finish( {"success":"false", "result":[], "total":-1, "error":retVal["Message"]} )
      return

    svcData = retVal[ 'Value' ]
    callback = {'success':'true', 'total' : svcData[ 'TotalRecords' ], 'result' : [] }
    now = Time.toEpoch()
    for record in svcData[ 'Records' ]:
      formatted = {}
      for i in range( len( svcData[ 'Fields' ] ) ):
        formatted[ svcData[ 'Fields' ][i].replace( ".", "_" ) ] = record[i]
      if 'activities_lastUpdate' in formatted:
        formatted[ 'activities_lastUpdate' ] = now - int( formatted[ 'activities_lastUpdate' ] )
      callback[ 'result' ].append( formatted )

    self.finish( callback )

  def __dateToSecs( self, timeVar ):
    dt = Time.fromString( timeVar )
    return int( Time.toEpoch( dt ) )

  @asyncGen
  def web_plotView( self ):

    plotRequest = {}
    try:
      if 'id' not in self.request.arguments:
        self.finish( { 'success' : "false", 'error' : "Missing viewID in plot request" } )
        return
      plotRequest[ 'id' ] = self.request.arguments[ 'id' ][0]
      if 'size' not in self.request.arguments:
        self.finish( { 'success' : "false", 'error' : "Missing plotsize in plot request" } )
        return
      plotRequest[ 'size' ] = int( self.request.arguments[ 'size' ][0] )

      timespan = int( self.request.arguments[ 'timespan' ][0] )
      if timespan < 0:
        toSecs = self.__dateToSecs( str( self.request.arguments[ 'toDate' ][0] ) )
        fromSecs = self.__dateToSecs( str( self.request.arguments[ 'fromDate' ][0] ) )
      else:
        toSecs = int( Time.toEpoch() )
        fromSecs = toSecs - timespan
      plotRequest[ 'fromSecs' ] = fromSecs
      plotRequest[ 'toSecs' ] = toSecs
      if 'varData' in self.request.arguments:
        plotRequest[ 'varData' ] = dict( json.loads( self.request.arguments[ 'varData' ][0] ) )
    except Exception, e:
      self.finish( { 'success' : "false", 'error' : "Error while processing plot parameters: %s" % str( e ) } )
      return

    rpcClient = RPCClient( "Framework/Monitoring" )
    retVal = yield self.threadTask( rpcClient.plotView, plotRequest )

    if retVal[ 'OK' ]:
      self.finish( { 'success' : "true", 'data' : retVal[ 'Value' ] } )
    else:
      self.finish( { 'success' : "false", 'error' : retVal[ 'Message' ] } )

  @asyncGen
  def web_getStaticPlotViews( self ):
    rpcClient = RPCClient( "Framework/Monitoring" )
    retVal = yield self.threadTask( rpcClient.getViews, True )
    if not retVal["OK"]:
      self.finish( {"success":"false", "error":retVal["Message"]} )
    else:
      self.finish( {"success":"true", "result":retVal["Value"]} )

  @asyncGen
  def web_getPlotImg( self ):
    """
    Get plot image
    """
    callback = {}
    if 'file' not in self.request.arguments:
      callback = {"success":"false", "error":"Maybe you forgot the file?"}
      self.finish( callback )
      return
    plotImageFile = str( self.request.arguments[ 'file' ][0] )
    if plotImageFile.find( ".png" ) < -1:
      callback = {"success":"false", "error":"Not a valid image!"}
      self.finish( callback )
      return
    transferClient = TransferClient( "Framework/Monitoring" )
    tempFile = tempfile.TemporaryFile()
    retVal = yield self.threadTask( transferClient.receiveFile, tempFile, plotImageFile )
    if not retVal[ 'OK' ]:
      callback = {"success":"false", "error":retVal[ 'Message' ]}
      self.finish( callback )
      return
    tempFile.seek( 0 )
    data = tempFile.read()
    self.set_header( 'Content-type', 'image/png' )
    self.set_header( 'Content-Length', len( data ) )
    self.set_header( 'Content-Transfer-Encoding', 'Binary' )
    self.finish( data )

  @asyncGen
  def web_queryFieldValue( self ):
    """
    Query a value for a field
    """
    fieldQuery = str( self.request.arguments[ 'queryField' ][0] )
    definedFields = json.loads( self.request.arguments[ 'selectedFields' ][0] )
    rpcClient = RPCClient( "Framework/Monitoring" )
    result = yield self.threadTask( rpcClient.queryField, fieldQuery, definedFields )
    if 'rpcStub' in result:
      del( result[ 'rpcStub' ] )

    if result["OK"]:
      self.finish( {"success":"true", "result":result["Value"]} )
    else:
      self.finish( {"success":"false", "error":result["Message"]} )

  @asyncGen
  def web_deleteActivities( self ):
    try:
      webIds = str( self.request.arguments[ 'ids' ][0] ).split( "," )
    except Exception, e:
      self.finish( {"success":"false", "error":"No valid id's specified"} )
      return

    idList = []
    for webId in webIds:
      try:
        idList.append( [ int( field ) for field in webId.split( "." ) ] )
      except Exception, e:
        self.finish( {"success":"false", "error":"Error while processing arguments: %s" % str( e )} )
        return

    rpcClient = RPCClient( "Framework/Monitoring" )

    retVal = yield self.threadTask( rpcClient.deleteActivities, idList )

    if 'rpcStub' in retVal:
      del( retVal[ 'rpcStub' ] )

    if retVal["OK"]:
      self.finish( {"success":"true"} )
    else:
      self.finish( {"success":"false", "error":retVal["Message"]} )

  @asyncGen
  def web_tryView( self ):
    """
    Try plotting graphs for a view
    """
    try:
      plotRequest = json.loads( self.request.arguments[ 'plotRequest' ][0] )
      if 'timeLength' in self.request.arguments:
        timeLength = str( self.request.arguments[ 'timeLength' ][0] )
        toSecs = int( Time.toEpoch() )
        if timeLength == "hour":
          fromSecs = toSecs - 3600
        elif timeLength == "day":
          fromSecs = toSecs - 86400
        elif timeLength == "month":
          fromSecs = toSecs - 2592000
        elif fromSecs == "year":
          fromDate = toSecs - 31104000
        else:
          self.finish( {"success":"false", "error":"Time length value not valid"} )
          return
      else:
        fromDate = str( self.request.arguments[ 'fromDate' ][0] )
        toDate = str( self.request.arguments[ 'toDate' ][0] )
        fromSecs = self.__dateToSecs( fromDate )
        toSecs = self.__dateToSecs( toDate )
    except Exception, e:
      self.finish( {"success":"false", "error":"Error while processing plot parameters: %s" % str( e )} )
      return

    rpcClient = RPCClient( "Framework/Monitoring" )
    requestStub = DEncode.encode( plotRequest )
    retVal = yield self.threadTask( rpcClient.tryView, fromSecs, toSecs, requestStub )
    if not retVal[ 'OK' ]:
      self.finish( {"success":"false", "error":retVal["Message"]} )
      return

    self.finish( {"success":"true", 'images' : retVal[ 'Value' ], 'stub' : requestStub} )

  @asyncGen
  def web_saveView( self ):
    """
    Save a view
    """
    try:
      plotRequest = json.loads( self.request.arguments[ 'plotRequest' ][0] )
      viewName = str( self.request.arguments[ 'viewName' ][0] )
    except Exception, e:
      self.finish( {"success":"false", "error": "Error while processing plot parameters: %s" % str( e )} )
    rpcClient = RPCClient( "Framework/Monitoring" )
    requestStub = DEncode.encode( plotRequest )
    result = yield self.threadTask( rpcClient.saveView, viewName, requestStub )
    if 'rpcStub' in result:
      del( result[ 'rpcStub' ] )

    self.finish( {"success":"true"} )

  def __getSections( self, path ):

    result = []

    userData = self.getSessionData()

    retVal = gConfig.getSections( '/DIRAC/Setups' )
    if retVal['OK']:
      setups = [ i.split( '-' )[-1] for i in retVal['Value']]
    setup = userData['setup'].split( '-' )[-1]
    leaf = True if path.find( 'Agents' ) != -1 or path.find( 'Services' ) != -1 else False
    retVal = gConfig.getSections( path )

    if retVal['OK']:
      records = retVal['Value']
      for i in records:
        if i in setups and i != setup:
          continue
        if i == setup:
          path = "%s/%s" % ( path, i )
          result = self.__getSections( path )

        if i not in [setup, 'Databases', 'URLs']:

          id = "%s/%s" % ( path, i )
          components = path.split( '/' )
          if len( components ) > 2:
            componentName = "%s/%s" % ( components[2], i )
          else:
            componentName = i
          result += [{'text':i, 'qtip': "Systems", "leaf" : leaf, 'component' : componentName, 'id':id}]
    else:
      result = []

    return result

  @asyncGen
  def web_getDynamicPlotViews( self ):
    """
    It retrieves the systems from the CS.
    """
    nodes = []
    path = self.request.arguments['node'][0]

    result = self.__getSections( path )
    print result
    for i in result:
      nodes += [i]

    result = tornado.escape.json_encode( nodes )
    self.finish( result )
