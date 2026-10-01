SELECT * from posts
JOIN users ON posts.user_id = users.user_id
WHERE first_name = 'Alice'