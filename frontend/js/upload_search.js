document.getElementById("displaytext").style.display = "none";
window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const synth = window.speechSynthesis;
const recognition = new SpeechRecognition();
const icon = document.querySelector('i.fa.fa-microphone')


function searchFromVoice() {
  recognition.start();
  recognition.onresult = (event) => {
    const speechToText = event.results[0][0].transcript;
    console.log(speechToText)
    document.getElementById("note-textarea").value = speechToText;

    var params = {
      "q": speechToText
    };
    var body = {};

    var additionalParams = {
      headers: {
        'Content-Type': "application/json",
        'x-api-key': 'FAtyYtn1u51h6a8OSy8xv75D3trxkuDP2vv967YT'
      }
    };

    searchGet(params,body,additionalParams);
  }
}

function searchGet(params, body, additionalParams){
  var apigClient = apigClientFactory.newClient({});
  apigClient.searchGet(params, body, additionalParams)
    .then(function (result) {
      console.log(result)
      //This is where you would put a success callback
      response_data = result.data
      var img1 = result.data;
      length_of_response = response_data.length;

      var images = result.data;
      images.forEach(x=>console.log(x))
      console.log(images[0])

      if (length_of_response == 0) {
        document.getElementById("displaytext").innerHTML = "No Images Found!"
        document.getElementById("displaytext").style.display = "block";
      }
      
      document.getElementById("img-container").innerHTML = "";
      var para = document.createElement("p");
      para.setAttribute("id", "displaytext")
      document.getElementById("img-container").appendChild(para);
      
      console.log(img1)

      img1.forEach(function (obj) {
        var img = new Image();
        img.src = obj;
        img.setAttribute("class", "banner-img");
        img.setAttribute("alt", "effy");
        img.setAttribute("width", "350");
        img.setAttribute("height", "350");
        img.setAttribute("style", "margin: 5px; border: 1px solid #555");
        document.getElementById("displaytext").innerHTML = "Images returned are : "
        document.getElementById("img-container").appendChild(img);
        document.getElementById("displaytext").style.display = "block";

      });
    }).catch(function (result) {
      //This is where you would put an error callback
    });
}


function searchPhoto() {
  var image_message = document.getElementById("note-textarea").value;
  // if(image_message == "")
  //   var image_message = document.getElementById("transcript").value;

  console.log(image_message);

  var body = {};
  var params = {
    q: image_message
  };
  var additionalParams = {
    headers: {
      'Content-Type': "application/json",
      'x-api-key': 'FAtyYtn1u51h6a8OSy8xv75D3trxkuDP2vv967YT'
    }
  };

  searchGet(params,body,additionalParams);

}

function uploadPhoto() {
  var file = document.getElementById('file_path').files[0];
  var customLabels = document.getElementById('image-labels').value;
  console.log('customLabels: '+customLabels)
  let config = {
       headers: { 
         'Content-Type': file.type,
         'x-amz-meta-customLabels':customLabels,
         'x-api-key': 'FAtyYtn1u51h6a8OSy8xv75D3trxkuDP2vv967YT' }
   };
   url = 'https://dpum01i045.execute-api.us-east-1.amazonaws.com/test/b2cloudbucket/' + file.name
   axios.put(url, file, config).then(response => {
      console.log(" New "+response.data)
     console.log("Success");
     document.getElementById("uploadText").innerHTML = "IMAGE UPLOADED SUCCESSFULLY!"
     document.getElementById("uploadText").style.display = "block";
     document.getElementById("uploadText").style.color = "black";
     document.getElementById("uploadText").style.fontWeight = "bold";
   });
}