<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <title>{{title}}</title>
    <link rel="SHORTCUT ICON" href='{{iconUrl}}'>

    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript" src="{{base_url}}/static/core/js/utils/canvg-1.3/rgbcolor.js"></script>
	  <script type="text/javascript" src="{{base_url}}/static/core/js/utils/canvg-1.3/StackBlur.js"></script>
	  <script type="text/javascript" src="{{base_url}}/static/core/js/utils/canvg-1.3/canvg.js"></script>
	  <script type="text/javascript" src="{{base_url}}/static/core/js/utils/FileSaver/FileSaver.js"></script>
	  
	<link rel="stylesheet" type="text/css" href="{{base_url}}/static/extjs/{{ext_version}}/resources/css/{{theme}}.css" />
    <link rel="stylesheet" type="text/css" href="{{base_url}}/static/extjs/resources/css/{{theme}}.css" />
    <link rel="stylesheet" type="text/css" href="{{base_url}}/static/core/css/css.css" />
    <link rel="stylesheet" type="text/css" href="{{base_url}}/static/core/css/iconset.css" />
    <link rel="stylesheet" type="text/css" href="{{base_url}}/static/core/css/TabScrollerMenu.css" />
    <link rel="stylesheet" type="text/css" href="{{base_url}}/static/core/css/tabtheme.css" />    
 
    {% autoescape None %}
    <!-- GC -->

    <!-- <x-compile> -->
    <!-- <x-bootstrap> -->

    {% if _dev %}
       {% if debug_level=='debug' %}
       	  <script type="text/javascript" src="{{base_url}}/static/extjs/{{ext_version}}/ext-all-dev.js"></script>
          <script type="text/javascript" src="{{base_url}}/static/extjs/ext-all-dev.js"></script>
       {% else %}
         <script type="text/javascript" src="{{base_url}}/static/extjs/ext-all.js"></script>
       {% end %}
    {% else %}
      <script type="text/javascript" src="{{base_url}}/static/core/build/all-classes.js"></script>
    {% end %}
    <!-- </x-bootstrap> -->
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart","annotatedtimeline"]});
      
      //Wrap console.log if it does not exist
      if (typeof console == "undefined") {
        window.console = {
          log: function () {}
        };
      }
     {% if _dev %}
       Ext.Loader.setConfig({
                   disableCaching: false
       });
       Ext.Loader.setPath({
       {% for extName in extensions %}
          {% if extName != 'WebAppDIRAC' %}
            {{ escape( extName ) }}: "{{ escape( '%s/static/%s' % ( base_url, extName ) ) }}",
          {% end %}
       {% end %}
            'Ext.dirac.core': '{{base_url}}/static/core/js/core',
            'Ext.dirac.views': '{{base_url}}/static/core/js/views',
            'Ext.dirac.utils': '{{base_url}}/static/core/js/utils',
            'Ext.ux.form':'{{base_url}}/static/extjs/{{ext_version}}/examples/ux/form',
            'Ext.ux':'{{base_url}}/static/extjs/{{ext_version}}/examples/ux'
          });

          Ext.require(['Ext.dirac.core.App','Ext.*']);

          var GLOBAL = {};

          GLOBAL.APP = null;
          GLOBAL.BASE_URL = "{{base_url}}/";
          GLOBAL.ROOT_URL = "{{root_url}}/";
          GLOBAL.EXTJS_VERSION = "{{ext_version}}";
          GLOBAL.DEV = 1;
          GLOBAL.URL_STATE = "{{url_state}}";
          GLOBAL.MOUSE_X = 0;
          GLOBAL.MOUSE_Y = 0;
          GLOBAL.IS_IE = false;
          {% import json %}
          GLOBAL.USER_CREDENTIALS = {{ json.dumps( credentials ) }};
          GLOBAL.WEB_THEME = "{{theme}}";
          GLOBAL.STATE_MANAGEMENT_ENABLED = true;
          GLOBAL.VIEW_ID = "{{view}}";
          GLOBAL.VALID_VIEWS = ["desktop","tabs"];
          GLOBAL.MAIN_VIEW_SAVE_STRUCTURE_VERSION = 1;
          GLOBAL.OPEN_APP = "{{open_app}}";
          GLOBAL.BACKGROUND = "{{backgroundImage}}";


          Ext.onReady(function () {
						Ext.override(Ext.data.Connection, { timeout:600000 });
						Ext.override(Ext.data.proxy.Ajax, { timeout:600000 });
            GLOBAL.APP = new Ext.dirac.core.App();
            setTimeout(function(){
              Ext.get("app-dirac-loading").hide();
              Ext.get("app-dirac-loading-msg").setHTML("Loading module. Please wait ...");
            },1000);
          });
      {% else %}
          var GLOBAL = {};

          GLOBAL.APP = null;
          GLOBAL.BASE_URL = "{{base_url}}/";
          GLOBAL.ROOT_URL = "{{root_url}}/";
          GLOBAL.EXTJS_VERSION = "{{ext_version}}";
          GLOBAL.DEV = 0;
          GLOBAL.URL_STATE = "{{url_state}}";
          GLOBAL.MOUSE_X = 0;
          GLOBAL.MOUSE_Y = 0;
          GLOBAL.IS_IE = false;
          {% import json %}
          GLOBAL.USER_CREDENTIALS = {{ json.dumps( credentials ) }};
          GLOBAL.WEB_THEME = "{{theme}}";
          GLOBAL.STATE_MANAGEMENT_ENABLED = true;
          GLOBAL.VIEW_ID = "{{view}}";
          GLOBAL.VALID_VIEWS = ["desktop","tabs"];
          GLOBAL.MAIN_VIEW_SAVE_STRUCTURE_VERSION = 1;
          GLOBAL.OPEN_APP = "{{open_app}}";
          GLOBAL.BACKGROUND = "{{backgroundImage}}";

          Ext.onReady(function () {
              Ext.override(Ext.data.Connection, { timeout:600000 });
				      Ext.override(Ext.data.proxy.Ajax, { timeout:600000 });
              GLOBAL.APP = new Ext.dirac.core.App();
              setTimeout(function(){
                Ext.get("app-dirac-loading").hide();
                Ext.get("app-dirac-loading-msg").setHTML("Loading module. Please wait ...");
              },1000);
          });
      {% end %}
    </script>
    <!-- </x-compile> -->
</head>

<body>
  <div id="app-dirac-loading">
      <div class="app-dirac-loading-indicator">
        <table>
          <tr>
            <td style="width:100px;">
              <img src="{{logo}}" style="margin-right:8px;float:left;vertical-align:top;width:100%;"/>
            </td>
            <td style="width:300px;vertical-align:middle;text-align:left;padding:5px 0px 5px 15px;font-size:14px">
              DIRAC
                <br />
                <span id="app-dirac-loading-msg">Loading data and resources...</span>
            </td>
          </tr>
        </table>
      </div>
  </div>

  <div id="app-dirac-welcome">
      <div class="app-dirac-welcome-text">
        <h1>Weclome to DIRAC!</h1>
        <b>D</b>istributed <b>I</b>nfrastructure with <b>R</b>emote <b>A</b>gent <b>C</b>ontrol INTERWARE is a software framework for distributed computing providing a complete solution to one (or more) user community requiring access to distributed resources. DIRAC builds a layer between the users and the resources offering a common interface to a number of heterogeneous providers, integrating them in a seamless manner, providing interoperability, at the same time as an optimized, transparent and reliable usage of the resources. 
        <a target="_blank" href="http://diracgrid.org">Discover more...</a>
        <div id="app-dirac-welcome-visitor">
          <h4>You are not registry!</h4>
          If you want to use a user proxy, we assume that you already have a user certificate, so in this case create a directory .globus in your home directory and copy the certificate files (public and pruvate keys in pem format) to this directory: 
          <br><code> $ mkdir ~/.globus 
          <br> $ cp /path/to/certificate_files ~/.globus/ </code>
          <br><br> At this point you need a proxy, you should do: 
          <br><code> $ dirac-proxy-init </code>
        </div>
      </div>
      <button id="app-dirac-welcome-close"> x </button>
      <div class="app-dirac-welcome-menu"> menu button </div>
      <div class="app-dirac-welcome-settings"> general settings </div>
  </div>
      

</body>
</html>