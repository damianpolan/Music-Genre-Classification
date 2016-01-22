class CreateRecordings < ActiveRecord::Migration
  def change
    create_table :recordings do |t|
      t.text :wav_path
      t.string :classified_as
      t.string :user_correct
      t.string :user_genre
      t.datetime :date

      t.timestamps null: false
    end
  end
end
