json.array!(@recordings) do |recording|
  json.extract! recording, :id, :wavblob, :classified_as, :user_correct, :user_genre, :date
  json.url recording_url(recording, format: :json)
end
