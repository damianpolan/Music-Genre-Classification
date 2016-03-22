# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://coffeescript.org/

# http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
# http://webaudio.github.io/web-audio-api/#ScriptProcessorNode


#Total recording time
RECORD_TIME = 10000
recording = false;

document.recordAndIdentify = () -> (
  if !recording
    recording = true
    UI_beginRecording()

    recordAudio (blob) -> (
      UI_endRecording()
      sendWavBlobForIdentification blob, (genre) -> (
        UI_endIdentification(genre)
        recording = false
      )
    )
)

UI_beginRecording = () -> (
  document.getElementById("progbar").hidden = false
  document.getElementById("record").innerHTML = " RECORDING "
  document.getElementById("record").className += " disabled"
)

UI_endRecording = () -> (
  document.getElementById("progbar").hidden = true
  document.getElementById("record").innerHTML = "identifying"
)

UI_endIdentification = (genre) -> (
  Materialize.fadeInImage('#genre')
  document.getElementById("genre").innerHTML = genre.toUpperCase()

  button = document.getElementById("record")
  button.innerHTML = "RECORD"
  button.className = button.className.replace(" disabled", "")
)


sendWavBlobForIdentification = (blob, callback) -> (
  reader = new window.FileReader()
  reader.onloadend = () -> (
    base64data = reader.result

    data = new FormData()
    data.append("wavblob", blob, (new Date()).getTime() + ".wav")

    http = new XMLHttpRequest()
    http.open("POST", "identify_song", true)
    http.onreadystatechange = () -> (
      if (http.readyState == 4 && http.status == 200)
        callback(http.responseText)
      else if (http.readyState == 4)
        callback("Error")
    )
    http.send(data)
  )
  reader.readAsDataURL(blob)
)


audioContext = null

recordAudio = (callback) ->
  """
    Records the users audio for time RECORD_TIME and returns a blob to the callback
  """
  if !navigator.getUserMedia
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
          navigator.mozGetUserMedia || navigator.msGetUserMedia

  if navigator.getUserMedia
    navigator.getUserMedia({audio:true},
      (mediaStream) -> (
#        document.setMessage("Recording")

        if !audioContext
          audioContext = new (window.AudioContext || window.webkitAudioContext)()

        inputPoint = audioContext.createGain()

        # Create an AudioNode from the stream.
        realAudioInput = audioContext.createMediaStreamSource(mediaStream)
        audioInput = realAudioInput
        audioInput.connect(inputPoint)

        analyserNode = audioContext.createAnalyser()
        analyserNode.fftSize = 2048
        inputPoint.connect( analyserNode )

        audioRecorder = new Recorder( inputPoint )

        zeroGain = audioContext.createGain()
        zeroGain.gain.value = 0.0
        inputPoint.connect( zeroGain )
        zeroGain.connect( audioContext.destination )

        audioRecorder.record();
        setTimeout () ->
          audioRecorder.stop()
          wavF = audioRecorder.exportWAV((blob) -> (
            Recorder.setupDownload(blob, "recording.wav")
            mediaStream.getAudioTracks()[0].stop()

            #send the file to the server
#            document.sendWavBlobForIdentification(blob)
            callback(blob)
          ))
        , RECORD_TIME
      )
    , (e) -> document.setMessage("Error capturing audio: " + e.name))
  else
    document.setMessage("No recording device found.")

document.setMessage = (message) ->
  Materialize.toast(message, 2000, 'rounded blue-grey darken-1')
