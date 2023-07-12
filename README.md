# To-do list website
A Flask application to store to-do lists and mark or delete items when done.
Bootstrap is used for all CSS.

Users have to register/login to utilize the application.<br>
The registration is handled with the Flask-login package.
The password is hashed (with werkzeug package) and then inserted in the database, so it's safer.<br>
The database is simple (just 3 schemes for users, lists and items), so it's created and handled with SQLite.

WTForm is used to handle all forms: registration, login, adding a new list and adding a new item to a list.
The latter two are pretty much the same codewise.

When a user logs in, all his/her lists are shown in reverse chronological order.
On the right of each row there's a button to delete the list (allowed only if it's empty).
Above the existing lists, a simple textbox allows to add a new list.

Clicking on a list, all its items are showns, following the same logic and features.
The only difference is that clicking on an item checks/unchecks it.
