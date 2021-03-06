import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO:DONE Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO:DONE Use the after_request decorator to set Access-Control-Allow
  '''
  #CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  '''
  @TODO:DONE
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    categories = {}
    try:
      selection = Category.query.order_by(Category.id).all()
      for category in selection:
            categories[category.id] = category.type
      return jsonify({
        'success': True,
        'categories': categories,
      })
    except:
      abort(405)

  '''
  @TODO:DONE
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    categories = {}
    current_category = []
    try:
      questions = Question.query.order_by(Question.category).all()
      current_questions = paginate_questions(request, questions)

      selection = Question.query.with_entities(Question.category).order_by(Question.category).all()
      for category in selection:
          for innerlist in category:
            current_category.append(innerlist)

      cat = Category.query.order_by(Category.id).all()
      for category in cat:
            categories[category.id] = category.type
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'categories': categories,
        'current_category': current_category
      })
    except:
      abort(405)
 
  '''
  @TODO:DONE
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()
      return jsonify({
        'success': True,
      })
    except:
      abort(422)

  '''
  @TODO:DONE
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    try: 
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = int(body.get('category', None))
      new_difficulty = int(body.get('difficulty', None))

      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      return jsonify({
      'success': True
    })
    except:
      abort(405)

  '''
  @TODO:DONE
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    current_category = []
    try:
      search = '%{}%'.format(search_term)
      selection = Question.query.order_by(Question.category).filter(Question.question.ilike(search)).all()
      questions = paginate_questions(request, selection)

      categories = Question.query.with_entities(Question.category).order_by(Question.category).filter(Question.question.ilike(search)).all()
      for category in categories:
        for innerlist in category:
          current_category.append(innerlist)

      return jsonify({
          'success': True,
          'questions': questions,
          'current_category': current_category,
          'total_questions': len(selection)
        })
    except:
      abort(422)

  '''
  @TODO:DONE
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def retrieve_questions_by_category(id):
    try: 
      selection = Question.query.order_by(Question.id).filter(Question.category == id).all() 
      questions = paginate_questions(request, selection)
      
      return jsonify({
          'success': True,
          'questions': questions,
          'current_category': id,
          'total_questions': len(selection)
        })  
    except:
      abort(405)

  '''
  @TODO:DONE
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_question_to_play():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    try:
      if quiz_category['id'] == 0:
        questions = Question.query.order_by(Question.id).all()
      elif (int(quiz_category['id']) in range(7)) and (int(quiz_category['id']) != 0):
        questions = Question.query.order_by(Question.id).filter(Question.category==int(quiz_category['id'])).all()

      selection = [question.format() for question in questions if question.id not in previous_questions]
      if len(selection) == 0: 
        return jsonify({
              'success': False,
              'question': False
            })
      return jsonify({
            'success':True,
            'question': random.choice(selection)
          })
    except:
      abort(400)

  '''
  @TODO:DONE 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resourse not found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'internal server errors'
    }), 500

  return app
