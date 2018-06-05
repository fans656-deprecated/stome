import React from 'react'

const todo = `\
Delete qiniu should be done in background (server side)

File thumbnail
  this can be done on server side like GET /girl/img/blue.jpg?thumbnail=64x64
  then on client side, query if imgage/jpeg etc

Uploading progress

Search

Move/Copy (drag / ctrl-c)

Selection rect

Shift/Ctrl selection

Image view

Arrow keys to navigate selection

====================== DONE

<Del> to delete

Global upload function

Directory size
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
