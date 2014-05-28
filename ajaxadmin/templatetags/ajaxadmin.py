from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def uploader(appname, parent_modelname, child_modelname, original, preview_width='"100%"', preview_height='"auto"'):
    parent_modelname = parent_modelname.lower()
    child_modelname = child_modelname.lower()
    url = reverse('admin:{}_{}_add'.format(appname, parent_modelname)) if not original else reverse(
        'admin:{}_{}_change'.format(appname, parent_modelname), args=[original.pk])
    return """
    <script>
    $(document).ready(function($) {{
        var token = $.cookie('csrftoken');

        $.ajaxSetup({{
          headers: {{'X-CSRFToken': token}}
        }});

    $("#multipleupload-{child_modelname}").uploadFile({{
            url: "{url}",
            multiple: true,
            fileName: "ajax",
            formData: {{action: "add", model: "{child_modelname}"}},
            showDone: false,
            showDelete: true,
            showDownload: true,
            showPreview: true,
            previewWidth: {preview_width},
            previewHeight: {preview_height},
            returnType: "json",
            downloadCallback:function(files, pd)
            {{
                window.open("/media/" + files[0], "Download");
            }},
            deleteCallback: function(data, pd)
            {{
                // now that seems to be a bug of jquery-upload-file
                if (typeof data == 'string') {{
                    data = JSON.parse(data);
                }}
                for(var i=0; i < data.length; i++)
                {{
                    $.post("{url}", {{action: "delete", model: "{child_modelname}", name: data[i]}},
                    function(resp, textStatus, jqXHR)
                    {{
                        console.log('ok')
                    }});
                 }}
                pd.statusbar.hide();

            }},
            {onload}
        }});
    }});
    </script>
    <div id="multipleupload-{child_modelname}">Upload</div>
    """.format(**{
        'parent_modelname': parent_modelname,
        'child_modelname': child_modelname,
        'appname': appname,
        'url': url,
        'preview_height': preview_height,
        'preview_width': preview_width,
        'onload': """
                    onLoad: function(obj)
                        {{
                            $.post("{url}", {{action: "get", model: "{child_modelname}"}},
                            function(resp, textStatus, jqXHR)
                            {{
                                var data = JSON.parse(resp);
                                for(var i=0; i < data.length; i++) {{
                                    obj.createProgress(data[i]['name']);
                                    // superhack to insert preview
                                    if (data[i]['thumbnail']) {{
                                        var preview = $($('.ajax-file-upload-statusbar').first().children()[0]);
                                        preview.attr('src', data[i]['thumbnail'])
                                        preview.show();
                                    }}
                                }}
                            }});
                       }}""".format(url=url, child_modelname=child_modelname) if original else "",
    })
