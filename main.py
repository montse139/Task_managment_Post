import os
import jinja2
import webapp2
from google.appengine.ext import ndb


class Task(ndb.Model):
    name = ndb.StringProperty()
    status = ndb.StringProperty()
    deadline = ndb.StringProperty()


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))



class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

    def post(self):
        name = self.request.get("name")
        status = self.request.get("status")
        deadline = self.request.get("deadline")

        task = Task(name=name, status=status, deadline=deadline)
        task.put()
        tasks = Task.query().fetch()
        params = {"tasks": tasks}
        return self.render_template("task_list.html", params=params)


class TaskListHandler(BaseHandler):
    def get(self):
        tasks = Task.query().fetch()
        params = {"tasks": tasks}
        return self.render_template("task_list.html", params=params)


class EditTaskHandler(BaseHandler):
    def get(self, task_id):
        task = Task.get_by_id(int(task_id))
        params = {"task": task}
        return self.render_template("task_edit.html", params=params)

    def post(self, task_id):
        new_name = self.request.get("name")
        new_status = self.request.get("status")
        new_deadline = self.request.get("deadline")
        task = Task.get_by_id(int(task_id))
        task.name = new_name
        task.status = new_status
        task.deadline = new_deadline
        task.put()
        return self.redirect_to("list")


class DeleteTaskHandler(BaseHandler):
    def get(self, task_id):
        task = Task.get_by_id(int(task_id))
        params = {"task": task}
        return self.render_template("task_delete.html", params=params)

    def post(self, task_id):
        task = Task.get_by_id(int(task_id))
        task.key.delete()
        return self.redirect_to("list")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/task_list', TaskListHandler, name="list"),
    webapp2.Route('/task_list/<task_id:\d+>/edit', EditTaskHandler),
    webapp2.Route('/task_list/<task_id:\d+>/delete', DeleteTaskHandler)
], debug=True)# Task_managment_Post
