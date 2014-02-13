#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from google.appengine.api import users

def getMainPage():
  return "<html><head>" +\
  getAutocomplete() +\
  """
   </head>
      <body>
       <form action="/trains" method="post">
         <H2><font color="red">Поиск билетов на РЖД</font></H2>
         <div class="ui-widget">
           <input class="suggest" id="from" type="search" name="from" size="30" placeholder="откуда" tabindex="0" required="true">
         </div>
         <br>
         <div class="ui-widget">
           <input class="suggest" id="to" type="search" name="to" size="30" placeholder="куда" tabindex="1" required="true">
         </div>
         <br>
         <div><input type="text" id="datepicker" name="date" tabindex="2" placeholder="дата" required="true" readonly="true"></div>
         <br>
         <div><input type="submit" value="мне повезет" tabindex="3"></div>
       </form>
  """ + getCurrentGoogleUser()+\
  """
     </body>
   </html>
  """

def getCurrentGoogleUser():
  user = users.get_current_user()
  if not user:      
      return '<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><font color="red">You are not looged in google or haven`t accout, </font><a href="%s">log in</a><br>' % users.create_login_url()
  else:
      return '<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><font color="red">Hello, %s, %s! </font>' % (user.nickname(), user.email())

def getAutocomplete():
  return """
  <meta charset="utf-8">
  <link rel="stylesheet" href="themes/jquery-ui.css">
  <link rel="stylesheet" href="themes/jquery-ui2.css">
  <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
  <script src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
  <link rel="stylesheet" href="themes/style.css">
  <style>
  .ui-autocomplete-loading {
    background: white url('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.1/themes/base/images/ui-anim_basic_16x16.gif') right center no-repeat;
  }


{ margin: 0; padding: 0; }

html { 
        background: url('themes/images/bg.jpg') no-repeat center center fixed; 
        -webkit-background-size: cover;
        -moz-background-size: cover;
        -o-background-size: cover;
        background-size: cover;
}

  </style>
  <script>
        $(function() {
          $( "#datepicker" ).datepicker();
        });

        (function ($) {
            $.fn.simpleSuggest = function (params) { // params - наши параметры, если не устраивают параметры по умолчанию
                params = params || {};
                var $elem = this, // сам элемент
                        options = { // параметры по умолчанию
                            search: function () {
                                // custom minLength
                                var term = extractLast(this.value);
                                if (term.length < 3) {
                                    return false;
                                }
                            },
                            focus: function () {
                                // prevent value inserted on focus
                                return false;
                            },
                            select: function (event, ui) {
                                var terms = split(this.value);
                                // remove the current input
                                terms.pop();
                                // add the selected item
                                terms.push(ui.item.value);
                                // add placeholder to get the comma-and-space at the end
                                //terms.push("");
                                //this.value = terms.join(", ");
                                this.value = terms;
                                return false;
                            }
                        };
                // смеживаем передаваемые параметры и стандартные параметры, но может стоит ограничиться просто заменой стандартного урла до бекэнда на пользоавтельский
                $.extend(options, params);

                $elem.on("keydown",function (event) {
                    if (event.keyCode === $.ui.keyCode.TAB &&
                            $(this).data("ui-autocomplete").menu.active) {
                        event.preventDefault();
                    }
                }).autocomplete(options);

                function split(val) {
                    return val.split(/,\s*/);
                }

                function extractLast(term) {
                    return split(term).pop();
                }
            };
        })(jQuery);

        // ждем когда загрузится страница
        $(document).ready(function () {
            // если хотим переопределить стандартные параметры, то можно их передать в вызов нашего плагина
            var params = {
                source: function (request, response) {
                    $.getJSON("suggester?lang=ru", {
                        stationNamePart: request.term.split(/,\s*/).pop()
                    }, response);
                }
            };

            // находим нужный элемент (элементы) и назначаем ему наш саджест
            $(".suggest").simpleSuggest(params);
        });

  </script>
  """