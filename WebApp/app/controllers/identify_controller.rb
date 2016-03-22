class IdentifyController < ApplicationController

  # don't check for authenticity
  skip_before_action :verify_authenticity_token


  def index
  end

  def contact

  end

  def classify

    puts "Classify"
    puts params[:wavblob]

    if params.has_key?(:wavblob)
      rec = Recording.new

      audio = params[:wavblob]
      audio.rewind

      save_path = Rails.root.join("private/recordings/#{audio.original_filename}")
      #save_path = Rails.root.join("private/recordings/recent.wav")

      rec.wav_path = save_path # set the wav_path of the Recording model

      File.open(save_path, 'wb') do |f|
        f.write audio.read
      end

      if rec.save
        # saved so continue with the classification
        cmd_s = "source /home/damian/Music-Genre-Classification/ENV/bin/activate;/home/damian/Music-Genre-Classification/ENV/bin/python2.7 /home/damian/Music-Genre-Classification/MGC-Source/mgc/trained/SVM_classify.py #{save_path}"
        puts cmd_s
        result = %x( #{cmd_s} )
        puts result
        render :text => result
      else
        render :text => "Failed to save recording"
      end
    else
      head :bad_request
    end
  end

end
