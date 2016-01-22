class IdentifyController < ApplicationController

  # don't check for authenticity
  skip_before_action :verify_authenticity_token


  def index
  end

  def classify

    puts "Classify"
    puts params[:wavblob]

    if params.has_key?(:wavblob)
      rec = Recording.new

      audio = params[:wavblob]
      audio.rewind

      save_path = Rails.root.join("private/recordings/#{audio.original_filename}")
      rec.wav_path = save_path # set the wav_path of the Recording model

      File.open(save_path, 'wb') do |f|
        f.write audio.read
      end

      if rec.save

        # saved so continue with the classification

        render :text => "Genre Here"
      else
        render :text => "Failed to save recording"
      end
    else
      head :bad_request
    end
  end

end
