(function ($) {
    var defaults = {
        rowsToDisplay: 10
    };
    
    var scrollBarWidth = 15, fixedTableWidth;
    
    $.fn.myfunction = function(options) {
        options = $.extend(defaults, options);
        
        var table = this;
        
        wrapTable(table, options);
        alignColumns(table);

        var resizeAlignFunction = function () { alignOnResize(table); };
        var canDebounce = typeof _ == 'function' && typeof _.debounce == 'function';
        if (canDebounce) resizeAlignFunction = _.debounce(resizeAlignFunction, 150);
        $(window).resize(resizeAlignFunction);
    };
    
    function wrapTable(table, options) {
        var existingClasses = table.attr('class');
        var existingMarginBottom = table.css('margin-bottom');
        table.css('margin-bottom', 0);
        var rowHeight = table.find('tbody tr:first').outerHeight();
        var tableHeight = rowHeight * options.rowsToDisplay;
        
        var headerTable = $('<table style="table-layout:fixed;width:auto;margin-bottom:0;" class="jqstb-header-table ' + existingClasses + '"><thead><tr><td></td></tr></thead></table>'),
            footerTable = $('<table style="table-layout:fixed;width:auto;margin-bottom:' + existingMarginBottom + ';" class="jqstb-footer-table ' + existingClasses + '"><tfoot><tr><td></td></tr></tfoot></table>'),
            scrollDiv = '<div class="jqstb-scroll" style="height:' + tableHeight + 'px;overflow-y:auto"></div>';
        
        // Insert the table that will hold the fixed header and footer, and insert the div that will get scrolled
        table.before(headerTable).before(scrollDiv).after(footerTable);
    }
    
    function alignColumns(table) {
        table.each(function (index) {
            // To minimize "Flash of Unstyled Content" (FOUC), set the relevant variables before manipulating the DOM
            var $dataTable = $(this);
            var $headerTable = $('table.jqstb-header-table').eq(index);
            var $footerTable = $('table.jqstb-footer-table').eq(index);
            
            // Place main table data inside of relevant scrollable div (using jQuery eq() and index)
            var $scrollDiv = $('div.jqstb-scroll').eq(index);
            $scrollDiv.prepend($dataTable);
            var scrollEl = $scrollDiv[0];
            
            var hasHorizontalScroll = scrollEl.clientWidth < scrollEl.scrollWidth;
            $scrollDiv.outerWidth(fixedTableWidth + scrollBarWidth + 2);
            
            if (hasHorizontalScroll) {
                var dataTableWidth = $dataTable.outerWidth();
                $headerTable.width(dataTableWidth);
                $footerTable.width(dataTableWidth);
                $scrollDiv.outerWidth(scrollEl.clientWidth);
                var scrollDivWidth = $scrollDiv.outerWidth();
                
                var width = scrollDivWidth - scrollBarWidth;
                
                var $headerScrollDiv = $('<div style="overflow:hidden;width:' + width + 'px" class="jqstb-header-scroll"></div>');
                $headerTable.wrap($headerScrollDiv);
                
                var $footerScrollDiv = $('<div style="overflow:hidden;width:' + width + 'px" class="jqstb-footer-scroll"></div>');
                $footerTable.wrap($footerScrollDiv);
                
                $scrollDiv.on('scroll', function() {
                    $('div.jqstb-header-scroll').scrollLeft($(this).scrollLeft());
                    $('div.jqstb-footer-scroll').scrollLeft($(this).scrollLeft());
                });
            }

            // Force column widths to be set for each header column
            $dataTable.find('thead tr:first th, tbody tr:first td').each(function () {
                $(this).outerWidth($(this).outerWidth());
            });
            
            // Insert header data into fixed header table
            $headerTable.find('thead').replaceWith($dataTable.children('caption, thead').clone());

            // Force column widths to be set for each footer column
            $dataTable.find('tfoot tr:first td').each(function () {
                $(this).outerWidth($(this).outerWidth());
            });
            
            // Insert footer data into fixed footer table
            $footerTable.find('tfoot').replaceWith($dataTable.children('tfoot').clone());
            
            // Hide original caption, header, and footer
            $dataTable.children('caption, thead, tfoot').hide();
        });
    }
    
    function alignOnResize(table) {
        table.each(function (index) {
            var $dataTable = $(this);
            var $headerTable = $('table.jqstb-header-table').eq(index);
            var $footerTable = $('table.jqstb-footer-table').eq(index);

            // Temporarily show the inner table's header and footer since the dom calculates width based on them being visible
            $dataTable.children('thead, tfoot').show();
            
            var scrollEl = $('div.jqstb-scroll')[0];
            var hasHorizontalScroll = scrollEl.clientWidth < scrollEl.scrollWidth;
            if (hasHorizontalScroll) {
                var scrollDivWidth = $('div.jqstb-scroll').outerWidth();
                $('div.jqstb-header-scroll').outerWidth(scrollDivWidth - scrollBarWidth);
                $('div.jqstb-footer-scroll').outerWidth(scrollDivWidth - scrollBarWidth);
            }
            
            // Force column widths to be set for each header column
            var $headerColumns = $headerTable.find('thead tr:first th');
            $dataTable.find('thead tr:first th').each(function (i) {
                $headerColumns.eq(i).outerWidth($(this).outerWidth());
            });

            // Force column widths to be set for each footer column
            var $footerColumns = $footerTable.find('tfoot tr:first td');
            $dataTable.find('tfoot tr:first td').each(function (i) {
                $footerColumns.eq(i).outerWidth($(this).outerWidth());
            });
            
            // Hide the inner table's header and footer when we're done 
            $dataTable.children('thead, tfoot').hide();
        });
    }
})(jQuery);

function addTitle() {
    this.event.preventDefault();
    let form = document.forms["personal_form"];
    let formElements = form.elements;
    console.log(formElements["moviepersonal"].value);
    addItem();
    return true;
}

function addItem() {
    var form = document.getElementById("personal_form");
    let formElements = form.elements;
    var formData = new FormData(form);
    formData.append('title', formElements["moviepersonal"].value);
    
    postAjaxAddTable('/add-title/', itemAdded, formData)
}

function submitTitles() {
    this.event.preventDefault();
    $("#rec_table tr:gt(0)").empty(); 
    var table = document.getElementById("personal_table");
    var formData = new FormData();
    var movieDict = {};
    for (var i = 1; i < table.rows.length - 1; i++) {
        var cells = table.rows.item(i).cells;
        movieDict['title'] = cells.item(0).innerHTML
        movieDict['tscore'] = cells.item(1).innerHTML
        movieDict['ascore'] = cells.item(2).innerHTML
        movieDict['oscars'] = cells.item(3).innerHTML
        movieDict['cscore'] = cells.item(4).innerHTML

        formData.append(i - 1, JSON.stringify(movieDict));
        movieDict = {}
    }
    postAjax('/submit-titles/', itemsSubmitted, formData);

    // for (var i = 0; i < formElements.length; i++) {
    //     var item = elements.item(i);
    //     console.log(item);
    // }
    // formData.append('title', formElements[]) 
}

function createXmlHttp() {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    } else {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (!(xmlhttp)) {
        alert("Your browser does not support AJAX!");
    }
    return xmlhttp;
}

function postAjax(url, callback, data) {
    var xmlHttp = createXmlHttp();
    xmlHttp.open("POST", url, true); // async
    // xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4) {
            console.log(xmlHttp.statusText)
            if (xmlHttp.status == 200) {
                console.log("[AJAX]: HTTP POST request success. url: " + url);
                if (callback) {
                    var obj = null;
                    try {
                        obj = JSON.parse(xmlHttp.responseText);
                        var table = document.getElementById("rec_table");
                        for (var key in obj) {
                            console.log(key, obj[key]);
                            var row = table.insertRow(1);
                            var title = row.insertCell(0);
                            var cscore = row.insertCell(1);
                            var tscore = row.insertCell(2);
                            var ascore = row.insertCell(3);
                            var oscars = row.insertCell(4);
                            title.innerHTML = obj[key]["title"];
                            cscore.innerHTML = obj[key]["cscore"];
                            tscore.innerHTML = obj[key]["tscore"];
                            ascore.innerHTML = obj[key]["ascore"];
                            oscars.innerHTML = obj[key]["oscars"];
                        }

                    } catch (e) {
                        console.log("[AJAX]: JSON parse failed! ResponseText:" + xmlHttp.responseText);
                    }
                    if (obj !== null) callback(obj);
                }
            } else {
                console.log("[AJAX]: HTTP POST request failed! url: " + url);
            }
        }
    }
    xmlHttp.send(data);
}

function postAjaxAddTable(url, callback, data) {
    var xmlHttp = createXmlHttp();
    xmlHttp.open("POST", url, true); // async
    // xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4) {
            console.log(xmlHttp.statusText)
            if (xmlHttp.status == 200) {
                console.log("[AJAX]: HTTP POST request success. url: " + url);
                if (callback) {
                    var obj = null;
                    try {
                        obj = JSON.parse(xmlHttp.responseText);
                        var table = document.getElementById("personal_table");
                        var row = table.insertRow(1);
                        var title = row.insertCell(0);
                        var cscore = row.insertCell(1);
                        var tscore = row.insertCell(2);
                        var ascore = row.insertCell(3);
                        var oscars = row.insertCell(4);
                        title.innerHTML = obj["title"];
                        cscore.innerHTML = obj["cscore"];
                        tscore.innerHTML = obj["tscore"];
                        ascore.innerHTML = obj["ascore"];
                        oscars.innerHTML = obj["oscars"];
                        //console.log(xmlhttp.responseText[0]);
                    } catch (e) {
                        console.log("[AJAX]: JSON parse failed! ResponseText:" + xmlHttp.responseText);
                    }
                    if (obj !== null) callback(obj);
                }
            } else {
                console.log("[AJAX]: HTTP POST request failed! url: " + url);
            }
        }
    }
    console.log(data);
    xmlHttp.send(data);
}

function itemAdded(result) {
    if (result.error) {
        console.log("Upload failed. Received error: " + result.error);
        alert("Upload failed. Received error: " + result.error);
        return;
    }
    console.log("Item uploaded.");
    document.getElementById("personal_form").reset();
    //alert("Upload success.");
    //location.reload();
}

function itemsSubmitted(result) {
    if (result.error) {
        console.log("Upload failed. Received error: " + result.error);
        alert("Upload failed. Received error: " + result.error);
        return;
    }
    $("#myModal").modal("show");
    console.log("Items submitted.");
    // document.getElementById("personal_form_table").remove();
    //alert("Upload success.");
    //location.reload();
}