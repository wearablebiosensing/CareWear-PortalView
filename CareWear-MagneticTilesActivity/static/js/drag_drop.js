class Shape {
  constructor(x, y, color) {
    this.x = x;
    this.y = y;
    this.color = color;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
  }

  draw() {
    // Abstract method - to be implemented in specific shape classes
  }

  isPointInside(x, y) {
    // Abstract method - to be implemented in specific shape classes
    return false;
  }

  mouseDown(x, y) {
    this.isDragging = true;
    this.startX = x;
    this.startY = y;
  }

  mouseUp() {
    this.isDragging = false;
  }

  mouseMove(x, y) {
    if (this.isDragging) {
      const dx = x - this.startX;
      const dy = y - this.startY;

      this.x += dx;
      this.y += dy;

      this.startX = x;
      this.startY = y;
    }
  }
}

class Square extends Shape {
  constructor(x, y, width, height, color) {
    super(x, y, color);
    this.width = width;
    this.height = height;
  }

  draw() {
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }

  isPointInside(x, y) {
    let shape_left = this.x;
    let shape_right = this.x + this.width;
    let shape_top = this.y;
    let shape_bottom = this.y + this.height;

    return (
      x > shape_left && x < shape_right && y > shape_top && y < shape_bottom
    );
  }
}

class Circle extends Shape {
  constructor(x, y, radius, color) {
    super(x, y, color);
    this.radius = radius;
  }

  draw() {
    ctx.beginPath();
    ctx.fillStyle = this.color;
    ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.closePath();
  }

  isPointInside(x, y) {
    return (
      Math.pow(this.x - x, 2) + Math.pow(this.y - y, 2) <=
      Math.pow(this.radius, 2)
    );
  }
}

class Trapezoid extends Shape {
  constructor(x, y, base, height, color) {
    super(x, y, color);
    this.base = base;
    this.height = height;
    this.x1 = x + base * 0.25;
    this.y1 = y;
    this.x2 = x + base * 0.75;
    this.y2 = y;
    this.x3 = x + base;
    this.y3 = y + height;
    this.x4 = x;
    this.y4 = y + height;
  }

  draw() {
    ctx.beginPath();
    ctx.moveTo(this.x1, this.y1);
    ctx.lineTo(this.x2, this.y2);
    ctx.lineTo(this.x3, this.y3);
    ctx.lineTo(this.x4, this.y4);
    ctx.closePath();
    ctx.fillStyle = this.color;
    ctx.fill();
  }

  mouseMove(x, y) {
    if (this.isDragging) {
      const dx = x - this.startX;
      const dy = y - this.startY;

      this.x += dx;
      this.y += dy;
      this.x1 += dx;
      this.y1 += dy;
      this.x2 += dx;
      this.y2 += dy;
      this.x3 += dx;
      this.y3 += dy;
      this.x4 += dx;
      this.y4 += dy;

      this.startX = x;
      this.startY = y;
    }
  }

  isPointInside(mouseX, mouseY) {
    const { x, y, x2, y2, x3, y3, x4, y4 } = this;

    // Calculate the cross products of the vectors from the point to each pair of adjacent vertices
    const crossProduct1 = (x2 - x) * (mouseY - y2) - (mouseX - x2) * (y2 - y);
    const crossProduct2 = (x3 - x2) * (mouseY - y2) - (mouseX - x2) * (y3 - y2);
    const crossProduct3 = (x4 - x3) * (mouseY - y3) - (mouseX - x3) * (y4 - y3);
    const crossProduct4 = (x - x4) * (mouseY - y4) - (mouseX - x4) * (y - y4);

    // Check if the point is on the same side of all four sides of the trapezoid
    const isInside =
      crossProduct1 >= 0 &&
      crossProduct2 >= 0 &&
      crossProduct3 >= 0 &&
      crossProduct4 >= 0;

    return isInside;
  }
}

class RightTriangle extends Shape {
  constructor(x, y, base, height, color) {
    super(x, y, color);
    this.base = base;
    this.height = height;
    this.x1 = x;
    this.y1 = y;
    this.x2 = x + base;
    this.y2 = y;
    this.x3 = x;
    this.y3 = y + height;
  }

  rotate90() {
    // Swap the base and height values
    const temp = this.base;
    this.base = this.height;
    this.height = temp;

    // Update the vertex coordinates accordingly
    this.x2 = this.x1 + this.base;
    this.y3 = this.y1 + this.height;
  }

  draw() {
    ctx.beginPath();
    ctx.moveTo(this.x1, this.y1);
    ctx.lineTo(this.x2, this.y2);
    ctx.lineTo(this.x3, this.y3);
    ctx.closePath();
    ctx.fillStyle = this.color;
    ctx.fill();
  }

  mouseMove(x, y) {
    if (this.isDragging) {
      const dx = x - this.startX;
      const dy = y - this.startY;

      this.x1 += dx;
      this.y1 += dy;
      this.x2 += dx;
      this.y2 += dy;
      this.x3 += dx;
      this.y3 += dy;

      this.startX = x;
      this.startY = y;
    }
  }

  isPointInside(mouseX, mouseY) {
    const { x1, y1, x2, y2, x3, y3 } = this;

    // Calculate the vectors from each vertex to the mouse position
    const vector1 = { x: mouseX - x1, y: mouseY - y1 };
    const vector2 = { x: mouseX - x2, y: mouseY - y2 };
    const vector3 = { x: mouseX - x3, y: mouseY - y3 };

    // Calculate the dot products of the vectors
    const dotProduct1 = vector1.x * (x2 - x1) + vector1.y * (y2 - y1);
    const dotProduct2 = vector2.x * (x3 - x2) + vector2.y * (y3 - y2);
    const dotProduct3 = vector3.x * (x1 - x3) + vector3.y * (y1 - y3);

    // Check if the dot products have the same sign
    const isInside = dotProduct1 >= 0 && dotProduct2 >= 0 && dotProduct3 >= 0;

    return isInside;
  }
}

//====================================
//          Canvas Settings
//====================================
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
canvas.width = 700;
canvas.height = 1000;

//====================================
//          Global Variables
//====================================
const shapes = [];
let current_shape_index = null;

shapes.push(new Square(0, 0, 100, 100, "orange"));
shapes.push(new Trapezoid(100, 200, 200, 100, "green"));
shapes.push(new Circle(300, 200, 50, "red"));
shapes.push(new RightTriangle(400, 300, 100, 100, "blue"));

//====================================
//             Utils
//====================================

function calculateMousePos(evt) {
  /* Function to calculate mouse coordinates relative to the canvas*/
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const x = (evt.clientX - rect.left) * scaleX;
  const y = (evt.clientY - rect.top) * scaleY;
  return { x, y };
}

//====================================
//          Block Options
//====================================
const shapeContainer = document.getElementById("shapeContainer");

shapeContainer.addEventListener("mousedown", function (event) {
  if (event.target.tagName === "IMG") {
    draggingImage = {
      image: event.target,
      offsetX: event.offsetX,
      offsetY: event.offsetY,
    };

    // Set the image element to be draggable
    event.target.draggable = true;

    // Add the necessary event listeners for the dragging behavior
    event.target.addEventListener("dragstart", dragStartHandler);
    event.target.addEventListener("dragend", dragEndHandler);
  }
});

function dragStartHandler(event) {
  draggingImage = {
    image: event.target,
    offsetX: event.offsetX,
    offsetY: event.offsetY,
  };

  // Set the image element to be dragged as a custom cursor
  event.dataTransfer.setDragImage(
    event.target,
    draggingImage.offsetX,
    draggingImage.offsetY
  );
}

function dragEndHandler(event) {
  const { x, y } = calculateMousePos(event);

  // Check if the mouse is released over the canvas
  if (x >= 0 && x <= canvas.width && y >= 0 && y <= canvas.height) {
    const shapeType = draggingImage.image.getAttribute("data-shape");

    let newShape;
    if (shapeType === "square") {
      newShape = new Square(
        x - draggingImage.offsetX,
        y - draggingImage.offsetY,
        100,
        100,
        "orange"
      );
    } else if (shapeType === "trapezoid") {
      newShape = new Trapezoid(
        x - draggingImage.offsetX,
        y - draggingImage.offsetY,
        200,
        100,
        "green"
      );
    }

    // Add the new shape to the shapes array
    shapes.push(newShape);

    // Redraw the canvas
    drawShapes();
  }

  draggingImage = null;
}

//====================================
//      Controls / EventListeners
//====================================
function mouse_down(event) {
  event.preventDefault();
  console.log("Mouse down - ", event);

  const { x, y } = calculateMousePos(event);

  // Check if the mouse is inside any shape
  for (let i = shapes.length - 1; i >= 0; i--) {
    const shape = shapes[i];
    if (shape.isPointInside(x, y)) {
      console.log("Inside of a shape");
      current_shape_index = i;
      shape.mouseDown(x, y);

      // Move the shape to the top of the stack
      //shapes.push(shapes.splice(i, 1)[0]);

      break;
    }
  }
}

function mouse_up(event) {
  console.log("UP");
  event.preventDefault();

  if (current_shape_index === null) return;

  shapes[current_shape_index].mouseUp();
  current_shape_index = null;
}

function mouse_move(event) {
  console.log("Mouse Move - ", event);
  if (current_shape_index === null) return;

  const { x, y } = calculateMousePos(event);
  shapes[current_shape_index].mouseMove(x, y);

  drawShapes();
}

canvas.addEventListener("mousedown", mouse_down);
canvas.addEventListener("mouseup", mouse_up);
canvas.addEventListener("mousemove", mouse_move);

//====================================
//          Game Functions
//====================================

function drawShapes() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let shape of shapes) {
    shape.draw();
  }
}

drawShapes();
