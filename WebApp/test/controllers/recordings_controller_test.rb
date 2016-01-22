require 'test_helper'

class RecordingsControllerTest < ActionController::TestCase
  setup do
    @recording = recordings(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:recordings)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create recording" do
    assert_difference('Recording.count') do
      post :create, recording: { classified_as: @recording.classified_as, date: @recording.date, user_correct: @recording.user_correct, user_genre: @recording.user_genre, wavblob: @recording.wavblob }
    end

    assert_redirected_to recording_path(assigns(:recording))
  end

  test "should show recording" do
    get :show, id: @recording
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @recording
    assert_response :success
  end

  test "should update recording" do
    patch :update, id: @recording, recording: { classified_as: @recording.classified_as, date: @recording.date, user_correct: @recording.user_correct, user_genre: @recording.user_genre, wavblob: @recording.wavblob }
    assert_redirected_to recording_path(assigns(:recording))
  end

  test "should destroy recording" do
    assert_difference('Recording.count', -1) do
      delete :destroy, id: @recording
    end

    assert_redirected_to recordings_path
  end
end
