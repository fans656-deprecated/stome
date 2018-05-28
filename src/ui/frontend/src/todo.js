import React from 'react'

const todo = `\
Directory size

File thumbnail
  this can be done on server side like GET /girl/img/blue.jpg?thumbnail=64x64
  then on client side, query if imgage/jpeg etc

Uploading progress

Search

Move/Copy (drag / ctrl-c)

Selection rect

Image view

<Del> to delete

Arrow keys to navigate selection
`;

const Todo = () => (
  <div style={{
    margin: '2em',
  }}>
    <h1>TODO</h1>
    <pre>{todo}</pre>
  </div>
)

export default Todo;
