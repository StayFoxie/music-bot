import gspread
from config import CREDENTIALS_FILENAME, QUESTIONS_SPREADSHEET_URL


class Quizzer:
    def __init__(self, question_spreadsheet_url=QUESTIONS_SPREADSHEET_URL):
        self.account = gspread.service_account(filename=CREDENTIALS_FILENAME)
        self.spreadsheet = self.account.open_by_url(question_spreadsheet_url)
        self.topics = {
            elem.title: elem.id for elem in self.spreadsheet.worksheets()
        }
        self.answers = self.spreadsheet.get_worksheet_by_id(self.topics.get("Results"))
        self.songs = self.spreadsheet.get_worksheet_by_id(self.topics.get("Song_list"))
        self.request = self.spreadsheet.get_worksheet_by_id(self.topics.get("Request_list"))

    def get_question_by_topic(self, topic_name):  # возвращает список, состоящий из вопросов
        if topic_name in self.topics:
            worksheet = self.spreadsheet.get_worksheet_by_id(self.topics.get(topic_name))
            return worksheet.get_all_records()
        return []

    def questions_and_answers(self):
        questions = self.get_question_by_topic(topic_name='Questions')
        result = []
        for elem in questions:
            answers = [elem["answer_1"],
                       elem["answer_2"],
                       elem["answer_3"]]
            new_format = {"question": elem["question"],
                          "answers": answers}
            result.append(new_format)
        return result

    def write_answer_to_result_cell(self, Username, AnswerSongLanguage, AnswerSongGenre, AnswerSongArtist):
        index = len(list(filter(None, self.answers.col_values(1)))) + 1
        self.answers.update(f"A{index}:E{index}", [[Username, AnswerSongLanguage, AnswerSongGenre, AnswerSongArtist]])

    def add_answer_to_request_list(self, Username, AnswerMood, AnswerDesiredEffect):
        index = len(list(filter(None, self.request.col_values(1)))) + 1
        self.request.update(f"A{index}:E{index}", [[Username, AnswerMood, AnswerDesiredEffect]])