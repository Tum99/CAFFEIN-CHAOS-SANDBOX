from flask import render_template
from app.events import events

@events.route('/events')
def all_events():
    return render_template('events/events.html')

@events.route('/events/<int:event_id>')
def event_details(event_id):
    return f"Details for event {event_id}"
