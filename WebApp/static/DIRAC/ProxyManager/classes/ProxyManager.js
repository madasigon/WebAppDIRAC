/*******************************************************************************
 * It is the transformation monitor class.
 */
Ext.define('DIRAC.ProxyManager.classes.ProxyManager', {
      extend : 'Ext.dirac.core.Module',
      requires : ['Ext.panel.Panel', 'Ext.panel.Panel', 'Ext.dirac.utils.DiracBoxSelect', 'Ext.dirac.utils.DiracToolButton', 'DIRAC.TransformationMonitor.classes.GridPanel', "Ext.form.field.TextArea", "Ext.dirac.utils.DiracGridPanel", 'Ext.dirac.utils.DiracIdListButton',
          'Ext.dirac.utils.DiracPageSizeCombo', 'Ext.dirac.utils.DiracPagingToolbar', 'Ext.dirac.utils.DiracJsonStore', 'Ext.dirac.utils.DiracAjaxProxy', 'Ext.dirac.utils.DiracApplicationContextMenu', 'Ext.dirac.utils.DiracBaseSelector'],

      loadState : function(data) {
        var me = this;

        me.grid.loadState(data);

        me.leftPanel.loadState(data);

        if (data.leftPanelCollapsed) {

          me.leftPanel.collapse();

        }

      },

      getStateData : function() {
        var me = this;
        var oStates = {};

        oStates = {
          grid : me.grid.getStateData(),
          leftMenu : me.leftPanel.getStateData()
        };

        oStates.leftPanelCollapsed = me.leftPanel.collapsed;

        return oStates;
      },
      dataFields : [{
            name : 'UserName'
          }, {
            name : 'UserDN'
          }, {
            name : 'UserGroup'
          }, {
            name : 'ExpirationTime',
            type : 'date',
            dateFormat : 'Y-m-d H:i:s'
          }, {
            name : 'PersistentFlag'
          }],

      initComponent : function() {
        var me = this;

        GLOBAL.APP.CF.log("debug", "create the widget(initComponent)...");

        me.launcher.title = "Proxy Manager";
        me.launcher.maximized = false;

        if (GLOBAL.VIEW_ID == "desktop") {

          var oDimensions = GLOBAL.APP.MAIN_VIEW.getViewMainDimensions();

          me.launcher.width = oDimensions[0];
          me.launcher.height = oDimensions[1];

          me.launcher.x = 0;
          me.launcher.y = 0;

        }

        Ext.apply(me, {
              layout : 'border',
              bodyBorder : false,
              defaults : {
                collapsible : true,
                split : true
              }
            });

        me.callParent(arguments);

      },
      buildUI : function() {

        var me = this;

        GLOBAL.APP.CF.log("debug", "create the widget...(buildUI)");

        var selectors = {
          username : "User",
          usergroup : "Group"
        };

        var map = [["username", "username"], ["usergroup", "usergroup"]];

        me.leftPanel = new Ext.create('Ext.dirac.utils.DiracBaseSelector', {
              scope : me,
              cmbSelectors : selectors,
              datamap : map,
              hasTimeSearchPanel : false,
              url : "ProxyManager/getSelectionData"
            });

        /*
         * -----------------------------------------------------------------------------------------------------------
         * DEFINITION OF THE GRID
         * -----------------------------------------------------------------------------------------------------------
         */
        var oProxy = Ext.create('Ext.dirac.utils.DiracAjaxProxy', {
              url : GLOBAL.BASE_URL + me.applicationName + "/getProxyManagerData"
            });

        me.diffValues = {};
        me.dataStore = Ext.create("Ext.dirac.utils.DiracJsonStore", {
              proxy : oProxy,
              fields : me.dataFields,
              groupField : 'UserName',
              scope : me
            });

        var pagingToolbar = null;

        var toolButtons = {
          'Visible' : [{
                "text" : "Delete",
                "handler" : me.__deleteProxyes,
                "properties" : {
                  tooltip : 'Click to delete the selected proxies!',
                  iconCls : "dirac-icon-delete"
                }
              }]
        };

        pagingToolbar = Ext.create("Ext.dirac.utils.DiracPagingToolbar", {
              toolButtons : toolButtons,
              store : me.dataStore,
              scope : me
            });

        var oColumns = {
          "checkBox" : {
            "dataIndex" : "proxyid"
          },
          "User" : {
            "dataIndex" : "UserName",
            "properties" : {
              width : 100,
              sortable : true
            }
          },
          "DN" : {
            "dataIndex" : "UserDN",
            "properties" : {
              width : 350,
              sortable : true
            }
          },
          "Group" : {
            "dataIndex" : "UserGroup",
            "properties" : {
              width : 100,
              sortable : true
            }
          },
          "Expiration date (UTC)" : {
            "dataIndex" : "ExpirationTime",
            "properties" : {
              width : 150,
              sortable : true
            },
            "renderer" : function(value, metadata, record, rowIndex, colIndex, store) {
              var expEpoch = record.data.ExpirationTime.getTime();
              var nowEpoch = Ext.Date.now();
              var secsLeft = expEpoch - nowEpoch;

              var msDay = 60 * 60 * 24 * 1000;
              var secsLeft = Math.floor((expEpoch - nowEpoch) / msDay);

              var timeLimit = 30; // 30 days before expiration

              if (secsLeft < timeLimit) {
                return '<span style="color:red">' + Ext.Date.format(record.data.ExpirationTime, "Y-m-d H:i:s")+' ('+secsLeft+')' + '</span>';
              } else {
                return '<span style="color:green">' + Ext.Date.format(record.data.ExpirationTime, "Y-m-d H:i:s") + '</span>';
              }

            }
          },
          "Persistent" : {
            "dataIndex" : "PersistentFlag",
            "properties" : {
              width : 100,
              sortable : true
            }
          }
        };

        me.grid = Ext.create('Ext.dirac.utils.DiracGridPanel', {
              store : me.dataStore,
              features : [{
                    ftype : 'grouping'
                  }],
              oColumns : oColumns,
              pagingToolbar : pagingToolbar,
              scope : me
            });

        me.leftPanel.setGrid(me.grid);

        me.add([me.leftPanel, me.grid]);

      },
      __deleteProxyes : function() {
        alert("Not implemented!!!");
      },
      __renderExpirationDate : function(value, metadata, record, rowIndex, colIndex, store) {
        var expStr = record.data.ExpirationTime.trim();
        var dayTime = expStr.split(" ");
        var expEpoch = new Date(dayTime[0]).getTime() / 1000;
        var nowEpoch = new Date().getTime() / 1000;
        var secsLeft = expEpoch - nowEpoch;
        var timeLimit = 86400 * 30; // 30 days before expiration
        if (secsLeft < 0) {
          secsLeft = 0;
        } else if (secsLeft > timeLimit) {
          secsLeft = timeLimit;
        }
        if (secsLeft < 3600) {
          var green = 0;
        } else {
          var green = 200;
        }
        var red = parseInt(255 * (timeLimit - secsLeft) / timeLimit);
        return '<span style="color: rgb(' + red + ',' + green + ',0);">' + expStr + '</span>';
      }
    });