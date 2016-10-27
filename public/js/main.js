$(document)
  .ready(function() {

    $("#generate-string")
      .click(function(e) {
        $.ajax({
          type: "POST",
          url: '/url',
          contentType: 'application/json',
          data: JSON.stringify({
            "url": $("input[name='form-input-url']")
              .val()
          }),
          success: function(data) {
            $("#the-string")
              .show();
            $('#shorturl-output a')
              .attr("href", data['urlcode-link'])
              .html(data['urlcode-link']);
          },
          dataType: 'json'
        });
        e.preventDefault();
      });

    $("input[name='form-input-url']")
      .on("keydown", function(e) {
        if (e.keyCode == 13) {
          $("#generate-string")
            .click();
        }
      });
  });
