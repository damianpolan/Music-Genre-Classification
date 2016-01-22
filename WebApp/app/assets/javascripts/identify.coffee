# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://coffeescript.org/

# http://typedarray.org/from-microphone-to-wav-with-getusermedia-and-web-audio/
# http://webaudio.github.io/web-audio-api/#ScriptProcessorNode


#Total recording time
RECORD_TIME = 1000

# http://stackoverflow.com/questions/27373620/saving-an-audio-blob-as-a-file-in-a-rails-app
document.sendWavBlobForIdentification = (blob) -> (
  console.log "Sending Wav File"

  reader = new window.FileReader()
  reader.onloadend = () -> (
    base64data = reader.result
    console.log(base64data)
    console.log base64data.length

    #params = "wavblob=" + base64data

    data = new FormData()
    data.append("wavblob", blob, (new Date()).getTime() + ".wav")

    http = new XMLHttpRequest()
    http.open("POST", "identify_song", true)
    # application/octet-stream multipart/form-data
    # http.setRequestHeader("Content-type", "multipart/form-data")
    http.onreadystatechange = () -> (
      if (http.readyState == 4 && http.status == 200)
        console.log(http.responseText)

    )
    http.send(data)
  )# application/octet-stream multipart/form-data
  reader.readAsDataURL(blob)
)

document.record = () ->

  if !navigator.getUserMedia
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
          navigator.mozGetUserMedia || navigator.msGetUserMedia

  if navigator.getUserMedia
    navigator.getUserMedia({audio:true},
      (mediaStream) -> (
        document.setMessage("Recording")
        context = new (window.AudioContext || window.webkitAudioContext)()
        inputPoint = context.createGain();

        # Create an AudioNode from the stream.
        realAudioInput = context.createMediaStreamSource(mediaStream)
        audioInput = realAudioInput
        audioInput.connect(inputPoint)

        analyserNode = context.createAnalyser()
        analyserNode.fftSize = 2048
        inputPoint.connect( analyserNode )

        audioRecorder = new Recorder( inputPoint );

        zeroGain = context.createGain();
        zeroGain.gain.value = 0.0;
        inputPoint.connect( zeroGain );
        zeroGain.connect( context.destination );

        audioRecorder.record();
        setTimeout () ->
          audioRecorder.stop()
          wavF = audioRecorder.exportWAV((blob) -> (
            console.log(blob)
            Recorder.setupDownload(blob, "recording.wav")
            mediaStream.getAudioTracks()[0].stop()

            #send the file to the server
            document.sendWavBlobForIdentification(blob)
          ))
        , RECORD_TIME
      )
    , (e) -> document.setMessage("Error capturing audio: " + e.name))


  else
    document.setMessage("No recording device found.")

document.setMessage = (message) ->
  Materialize.toast(message, 2000, 'rounded blue-grey darken-1')



# manual recording code
#    navigator.getUserMedia({audio:true},
#      (mediaStream) -> (
#        document.setMessage("Recording")
#        # the source input of the mediaStream is the device microphone
#        console.log mediaStream
#        console.log mediaStream.getAudioTracks()
#        audioStreamTrack = mediaStream.getAudioTracks()[0]
#
#
#        context = new (window.AudioContext || window.webkitAudioContext)()
#        sampleRate = context.sampleRate
#        volume = context.createGain()
#        audioInput = context.createMediaStreamSource(mediaStream) # creates a MediaStreamAudioSourceNode
#        audioInput.connect(volume)
#
#        bufferSize = 2048
#        leftchannel = []
#        rightchannel = []
#        recordingLength = 0
#
#        recorder = context.createScriptProcessor(bufferSize, 2, 2)
#        recorder.onaudioprocess = (audioProcessingEvent) -> (
#          left = audioProcessingEvent.inputBuffer.getChannelData 0
#          right = audioProcessingEvent.inputBuffer.getChannelData 1
#          leftchannel.push(new Float32Array (left))
#          rightchannel.push(new Float32Array (right))
#          recordingLength += bufferSize
#        )
#
#        volume.connect(recorder)
#        recorder.connect(context.destination)
#
#
#
#        audioStreamTrack.onended = () -> (
#          mergeBuffers = (channelBuffer, recordingLength) -> (
#            result = new Float32Array(recordingLength)
#            offset = 0
#            lng = channelBuffer.length
#            for i in [0 ... lng]
#              buffer = channelBuffer[i]
#              result.set(buffer, offset)
#              offset += buffer.length
#            return result
#          )
#          leftchannel = mergeBuffers(leftchannel, recordingLength)
#          rightchannel = mergeBuffers(rightchannel, recordingLength)
#
#          for item in leftchannel
#            if item != 0
#              document.setMessage(item)
#          for item in rightchannel
#            if item != 0
#              document.setMessage(item)
#
#          document.setMessage("Done.")
#        )
#
#        setTimeout () ->
#          recorder.disconnect()
#          audioStreamTrack.stop()
#
#        , RECORD_TIME
#      )
#    , (e) ->
#      document.setMessage("Error capturing audio: " + e.name))