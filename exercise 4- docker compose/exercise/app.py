 
from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Professor, ResearchGroup, Student
import json
from bson.objectid import ObjectId
import os
import logging

app = Flask(__name__)

# database configs
app.config['MONGODB_SETTINGS'] = {
    # set the correct parameters here as required, some examples aer give below
    #'host':'mongodb+srv://fullstack-course:asdfghjkl@cluster0.e8nyj.mongodb.net/flask-db?retryWrites=true&w=majority'
    'host':'mongodb://mongo:27017/flask-db'
}
db = initialize_db(app)

# Root
@app.route('/')
def get_route():
    output = {'message': 'It looks like you are trying to access FlaskAPP over HTTP on the native driver port.'}
    return output, 200

# Update the methods below
@app.route('/listStudent/<student_id>', methods=['GET','PUT','DELETE'])
def get_student_by_id(student_id):
    
    if request.method == "GET":
        student = Student.objects.get(id=student_id)
        if student:
            # Update Code here
            rgroupIds = []
            for rg in student.researchGroups:
                rgroupIds.append(str(rg.id))
            output = {'name': student['name'], 'studentNumber': student['studentNumber'], 'researchGroups': rgroupIds}
            status_code = 200
        else:
            # Update Code here
            
            output = {'message': 'Student not found'}
            status_code = 404
        return output, status_code
    elif request.method == "PUT":
        body = request.get_json()
        keys = body.keys()
        if body and keys:
            Student.objects.get(id=student_id).update(**body)
            
            output = {'message': 'Student successfully updated', 'id': student_id}
            status_code = 200
        else:
            # Update Code here
            
            output = {'message': 'Message body empty'}
            status_code = 204
        return output, status_code
    elif request.method == "DELETE":
        # Update Code here

        Student.objects.get_or_404(id=student_id).delete()
        output = {'message': 'Student successfully deleted', 'id': student_id}
        status_code = 200
        return output, status_code


# Complete the  request methods below
@app.route('/listStudent', methods=['POST']) 
def add_student():

    # Update the code here.      
    body = request.get_json()
    student = Student(**body).save()
    output = {'message': "Student successfully created", 'id': str(student.id)}
    # Update the status code
    status_code = 201
    return output, status_code


@app.route('/listStudents') 
def get_all_students():
    """
    This function lists all students
    """
    try:
        gname = request.args.get('groupName')

        if gname:
            logging.error(gname)
            grp = ResearchGroup.objects.get(name=gname)
            students = Student.objects(researchGroups=grp)
            output = []
            for st in students:
                output.append({'name': st.name, 'studentNumber': st.studentNumber})
        else:
            output = {'message': 'Empty or Invalid body'}
        
        return Response(json.dumps(output), mimetype='application/json', status=200)
    except Exception as e:
        logging.exception(e)
        output = {'message': 'Server Error'}
        return output, 500



@app.route('/listGroup/<group_id>',  methods=['GET','PUT','DELETE'])
def get_researchgroup_by_id(group_id):
    if request.method == "GET":
        researchGroup = ResearchGroup.objects.get(id=group_id)
        logging.error(researchGroup['founder'])
        if researchGroup:
            # Update Code here
            
            output = {'id':group_id,'name': researchGroup['name'], 'founder': str(researchGroup['founder'].id)}
            status_code = 200
        else:
            # Update Code here
            
            output = {'message': 'ResearchGroup not found'}
            status_code = 404
        return output, status_code
    elif request.method == "PUT":
        try:
            body = request.get_json()
            grp = ResearchGroup.objects.get_or_404(id=group_id)

            new_founder = Professor.objects.get(id=body.get('founder')) if body.get('founder') is not None else grp.founder

            grp.update(**{
                'name': body.get('name', grp.name),
                'description': body.get('description', grp.description),
                'founder': new_founder
            })
            grp.save()
            output = {'message': 'Group successfully updated', 'id': group_id}
            return Response(json.dumps(output), mimetype='application/json', status=200)
        except Exception as e:
            logging.exception(e)
            output = {'message': 'Server Error'}
            return output, 500
    elif request.method == "DELETE":
        # Update Code here

        ResearchGroup.objects.get_or_404(id=group_id).delete()
        output = {'message': 'Group successfully deleted', 'id': group_id}
        status_code = 200
        return output, status_code

@app.route('/listGroup', methods=['POST']) 
def add_group():

    # Update the code here.      
    body = request.get_json()
    group = ResearchGroup(**body).save()
    output = {'message': "Group successfully created", 'id': str(group.id)}
    # Update the status code
    return Response(json.dumps(output), mimetype='application/json', status=201)

@app.route('/listProfessor/<prof_id>',  methods=['GET','PUT','DELETE'])
def get_prof_by_id(prof_id):
    if request.method == "GET":
        professor = Professor.objects.get(id=prof_id)
        if professor:
            # Update Code here
            
            output = {'name': professor['name'], 'email': professor['email'], 'designation': professor['designation'], 'interests': professor['interests']}
            status_code = 200
        else:
            # Update Code here
            
            output = {'message': 'Professor not found'}
            status_code = 404
        return output, status_code
    elif request.method == "PUT":
        body = request.get_json()
        professor = Professor.objects.get_or_404(id=prof_id)
        logging.error(professor.researchGroups)
        logging.error(body.get('researchGroups'))
        keys = body.keys()
        if body and keys:
            rgroups = []
            for rgs in body.get('researchGroups'):
                rgroups.append(ResearchGroup.objects.get(id=rgs))
            professor.update(**{
                'name': body.get('name', professor.name),
                'email': body.get('email', professor.email),
                'designation': body.get('designation', professor.designation),
                'interests': body.get('interests', professor.interests),
                'researchGroups': rgroups,
            })
            professor.save()
            
            output = {'message': 'Professor successfully updated', 'id': prof_id}
            status_code = 200
        else:
            # Update Code here
            
            output = {'message': 'Message body empty'}
            status_code = 204
        return output, status_code
    elif request.method == "DELETE":
        # Update Code here

        Professor.objects.get_or_404(id=prof_id).delete()
        output = {'message': 'Professor successfully deleted', 'id': prof_id}
        status_code = 200
        return output, status_code

@app.route('/listProfessor', methods=['POST']) 
def add_professor():

    # Update the code here.      
    body = request.get_json()
    professor = Professor(**body).save()
    output = {'message': "Professor successfully created", 'id': str(professor.id)}
    # Update the status code
    status_code = 201
    return output, status_code


@app.route('/listGroups') 
def get_all_groups():
    """
    This function lists all groups
    """

    groups = ResearchGroup.objects().to_json()
    output = groups
    # Update the status code
    status_code = 200
    return output, status_code

@app.route('/listProfessors') 
def get_all_professors():
    try:
        designation = request.args.get('designation')
        gname = request.args.get('groupName')

        if designation or gname:
            logging.error(designation)
            logging.error(gname)
            output = []
            if gname:
                grp = ResearchGroup.objects.get_or_404(name=gname)
                professors = Professor.objects(researchGroups=grp)
                for prof in professors:
                    output.append({'name': prof.name, 'email': prof.email})
            elif designation:
                professors = Professor.objects(designation=designation)
                for prof in professors:
                    output.append({'name': prof.name, 'email': prof.email})
            else:
                output = {'message': 'Keyword not found'}
        else:
            output = {'message': 'Message body empty'}
        
        return Response(json.dumps(output), mimetype='application/json', status=200)
    except Exception as e:
        logging.exception(e)
        output = {'message': 'Server Error'}
        return output, 500

# Only for local testing without docker
#app.run() # FLASK_APP=app.py FLASK_ENV=development flask run