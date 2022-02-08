    $(document).ready(function () {


        $('form').on('submit', function (event) {
            $.ajax({
                data: {
                    click: 'Capture',
                    uid: $('#uid').val()
                },
                type: 'post',
                url: '/requests'
            })
            document.getElementById('ipform').reset()
        });

         function fetchMatchedProfilesData(){
             fetch('/get_similarity_json').then(response => {
                 if(response.status == 200){
                     response.json().then(data => {
                        console.log(data);
                        console.log(Object.keys(data).length);
                         $("#pid").text(data['id']);
                         $("#name").text(data['name']);
                         $("#confidence").text('99%');
                         $("#current_image").attr("src", data['cr_img']);
                         $("#db_image").attr("src", data['db_img']);
                         setTimeout(()=>fetchMatchedProfilesData(),2000);
                     });
                 }
                 else if(response.status == 404 || response.status == 500){
                     $("#pid").text("----");
                     $("#name").text("----");
                     $("#confidence").text("----");
                     $("#db_image").attr("src", "static/data/dummy.png");
                     $("#current_image").attr("src", "static/data/dummy.png");

                     setTimeout(()=>fetchMatchedProfilesData(),2000);
                 }
             }).catch(error => {});
         }

         fetchMatchedProfilesData();

























//         function fetchLogData() {
//             $.ajax({
//                 url: "/get_log_json",
//                 contentType: 'application/json',
//                 success: function (data){
// <!--                    console.log(data.Date);-->
//                     $("#logs").replaceWith('<p class="card-text" id="logs"> </p>');
//                     //or to list all values
//                     for(var i = 0; i < data.Date.length; i++){
//                          $("#logs").append("<p>"+ data.Date[i] + " | " + data.Time[i] + "</p> <br>");
//                     }

//                     setTimeout(()=>resetLogs(),2000);
//                 }
//             });
//         }

//         function fetchMatchedProfilesData(){
//             fetch('/get_similarity_json').then(response => {
//                 if(response.status == 200){
//                     response.json().then(data => {
//                         if ((Object.keys(data).length) == 1){
//                             console.log(data);
//                             $("#pid").text(data[0][0]);
//                             $("#name").text(data[0][1]);
//                             $("#confidence").text(data[0][2]);
//                             $("#current_image").attr("src", data[0][3]);
//                             $("#db_image").attr("src", data[0][4]);

//                             fetchLogData();
//                         }
//                         // else{
//                         //     console.log(data);
//                         //     $("#pid").text("----");
//                         //     $("#name").text("Unknown");
//                         //     $("#confidence").text("----");
//                         //     $("#current_image").attr("src", data[0][3]);
//                         //     $("#db_image").attr("src", "static/data/unknown.png");
//                         //
//                         //     $("#sname1").text(data[0][1]);
//                         //     $("#db_image1").attr("src", data[0][4]);
//                         //
//                         //     $("#sname4").text(data[1][1]);
//                         //     $("#db_image4").attr("src", data[1][3]);
//                         //
//                         //     $("#sname2").text(data[2][1]);
//                         //     $("#db_image2").attr("src", data[2][3]);
//                         //
//                         //     $("#sname3").text(data[3][1]);
//                         //     $("#db_image3").attr("src", data[3][3]);
//                         // }
//                         setTimeout(()=>fetchMatchedProfilesData(),2000);
//                     });
//                 }
//                 else if(response.status == 404 || response.status == 500){
//                     $("#pid").text("----");
//                     $("#name").text("----");
//                     $("#confidence").text("----");
//                     $("#db_image").attr("src", "static/data/dummy.png");
//                     $("#current_image").attr("src", "static/data/dummy.png");

//                     $("#sname1").text("----");
//                     $("#db_image1").attr("src", "static/data/dummy.png");

//                     $("#sname2").text("----");
//                     $("#db_image2").attr("src", "static/data/dummy.png");

//                     $("#sname3").text("----");
//                     $("#db_image3").attr("src", "static/data/dummy.png");

//                     $("#sname4").text("----");
//                     $("#db_image4").attr("src", "static/data/dummy.png");

//                     setTimeout(()=>fetchMatchedProfilesData(),2000);
//                 }
//             }).catch(error => {});
//         }

//         function resetLogs(){
//             $("#logs").replaceWith('<p class="card-text" id="logs"> </p>');
//         }

//         fetchMatchedProfilesData();

    });