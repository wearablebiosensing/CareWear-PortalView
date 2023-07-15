class Shape {
  constructor(x, y, color, isLevelShape) {
    this.x = x;
    this.y = y;
    this.color = color;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.isLevelShape = isLevelShape; // Flag to indicate if it's a special shape
    this.isLevelShapeFilled = false; //Flag to indicate if a level shape is already filled
    this.isSnapped = false; // Flag to track if a shape is snapped to this target
    this.snapDistanceThreshold = 50; //Flag to indicate how close a shape must be to Level shape to snap to it
  }

  draw() {
    // Abstract method - to be implemented in specific shape classes
  }

  isPointInside(x, y) {
    // Abstract method - to be implemented in specific shape classes
    return false;
  }

  snapToTargetShape(targetShape) {}

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
  constructor(x, y, width, height, color, isLevelShape = false) {
    super(x, y, color, isLevelShape);
    this.width = width;
    this.height = height;
    this.rotation = 0;
  }

  draw() {
    // ctx.fillStyle = this.isSnapped ? "green" : this.color;
    //ctx.globalAlpha = this.isSnapped ? 0.5 : 1; //Adjust transparency;
    // ctx.fillRect(this.x, this.y, this.width, this.height);
    //ctx.globalAlpha = 1; // Reset the global alpha value

    ctx.save(); // Save the current transformation state
    ctx.translate(this.x + this.width / 2, this.y + this.height / 2); // Translate the coordinate system to the center of the square
    ctx.rotate((Math.PI / 180) * this.rotation); // Rotate the coordinate system by the specified angle
    ctx.fillStyle = this.isSnapped ? "green" : this.color;
    ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height); // Draw the square centered at the translated coordinates
    ctx.restore(); // Restore the previous transformation state
  }

  snapToTargetShape(targetShape) {
    //Prevents an already filled tile shape from being use again
    if (targetShape.isLevelShapeFilled) return;

    if (targetShape instanceof Square) {
      // Snap Square shape to target Square shape if they are close enough
      const distance = Math.sqrt(
        Math.pow(this.x - targetShape.x, 2) +
          Math.pow(this.y - targetShape.y, 2)
      );
      if (distance <= this.snapDistanceThreshold) {
        this.x = targetShape.x;
        this.y = targetShape.y;
        this.isSnapped = true;
        targetShape.isLevelShapeFilled = true;
        this.mouseUp();
      }
    }
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
  constructor(x, y, radius, color, isLevelShape = false) {
    super(x, y, color, isLevelShape);
    this.radius = radius;
  }

  draw() {
    ctx.beginPath();
    ctx.fillStyle = this.isSnapped ? "green" : this.color;
    ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.closePath();
  }

  snapToTargetShape(targetShape) {
    //Prevents an already filled tile shape from being use again
    if (targetShape.isLevelShapeFilled) return;

    if (targetShape instanceof Circle) {
      // Snap Circle shape to target Circle shape if they are close enough

      const distance = Math.sqrt(
        Math.pow(this.x - targetShape.x, 2) +
          Math.pow(this.y - targetShape.y, 2)
      );
      if (distance <= this.snapDistanceThreshold) {
        this.x = targetShape.x;
        this.y = targetShape.y;
        this.isSnapped = true;
        targetShape.isLevelShapeFilled = true;
        this.mouseUp();
      }
    }
  }

  isPointInside(x, y) {
    return (
      Math.pow(this.x - x, 2) + Math.pow(this.y - y, 2) <=
      Math.pow(this.radius, 2)
    );
  }
}

class Trapezoid extends Shape {
  constructor(x, y, base, height, color, isLevelShape = false) {
    super(x, y, color, isLevelShape);
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
    ctx.fillStyle = this.isSnapped ? "green" : this.color;
    ctx.fill();
  }

  snapToTargetShape(targetShape) {
    //Prevents an already filled tile shape from being use again
    if (targetShape.isLevelShapeFilled) return;

    if (targetShape instanceof Trapezoid) {
      // Snap Trapezoid shape to target Trapezoid shape if they are close enough

      // Calculate the distance between the centers of the trapezoids
      const centerX = this.x + (this.x3 - this.x) / 2;
      const centerY = this.y + (this.y3 - this.y) / 2;
      const targetCenterX =
        targetShape.x + (targetShape.x3 - targetShape.x) / 2;
      const targetCenterY =
        targetShape.y + (targetShape.y3 - targetShape.y) / 2;
      const distance = Math.sqrt(
        Math.pow(centerX - targetCenterX, 2) +
          Math.pow(centerY - targetCenterY, 2)
      );

      if (distance <= this.snapDistanceThreshold) {
        // Snap the Trapezoid shape to the target Trapezoid shape
        const dx = targetShape.x - this.x;
        const dy = targetShape.y - this.y;
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

        this.isSnapped = true;
        targetShape.isLevelShapeFilled = true;
        this.mouseUp();
      }
    }
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
  constructor(x, y, base, height, color, rotation = 0, isLevelShape = false) {
    super(x, y, color, isLevelShape);
    this.base = base;
    this.height = height;
    this.x1 = x;
    this.y1 = y;
    this.x2 = x + base;
    this.y2 = y;
    this.x3 = x;
    this.y3 = y + height;
    this.rotation = rotation;
  }

  draw() {
    ctx.save(); // Save the current transformation state

    ctx.translate(this.x + this.base / 2, this.y + this.height / 2); // Translate the coordinate system to the center of the right triangle
    ctx.rotate((Math.PI / 180) * this.rotation); // Rotate the coordinate system by the specified angle

    ctx.beginPath();
    ctx.moveTo(-this.base / 2, -this.height / 2);
    ctx.lineTo(this.base / 2, -this.height / 2);
    ctx.lineTo(-this.base / 2, this.height / 2);
    ctx.closePath();

    ctx.fillStyle = this.isSnapped ? "green" : this.color;
    ctx.fill();

    ctx.restore(); // Restore the previous transformation state
  }

  snapToTargetShape(targetShape) {
    //Prevents an already filled tile shape from being use again
    if (targetShape.isLevelShapeFilled) return;

    if (targetShape instanceof RightTriangle) {
      if (this.rotation % 360 != targetShape.rotation % 360) return; //Have to be same rotation

      // Snap RightTriangle shape to target RightTriangle shape if they are close enough

      // Calculate the distance between the centers of the triangles
      const centerX = this.x + (this.x1 + this.x2) / 2;
      const centerY = this.y + (this.y1 + this.y3) / 2;
      const targetCenterX =
        targetShape.x + (targetShape.x1 + targetShape.x2) / 2;
      const targetCenterY =
        targetShape.y + (targetShape.y1 + targetShape.y3) / 2;
      const distance = Math.sqrt(
        Math.pow(centerX - targetCenterX, 2) +
          Math.pow(centerY - targetCenterY, 2)
      );

      if (distance <= this.snapDistanceThreshold) {
        // Snap the RightTriangle shape to the target RightTriangle shape
        const dx = targetShape.x - this.x;
        const dy = targetShape.y - this.y;
        this.x += dx;
        this.y += dy;
        this.x1 += dx;
        this.y1 += dy;
        this.x2 += dx;
        this.y2 += dy;
        this.x3 += dx;
        this.y3 += dy;

        this.isSnapped = true;
        targetShape.isLevelShapeFilled = true;
        this.mouseUp();
      }
    }
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
let mouse_motion_array = [];
let mouse_motion_accumulator = 0;
const mouse_motion_collect_interval = 10;

//====================================
//              Levels
//====================================
const LEVEL_1 = [];

LEVEL_1.push(new Square(350, 400, 100, 100, "grey", true)); // Right Middle
LEVEL_1.push(new Square(350, 290, 100, 100, "grey", true)); //Left Middle
LEVEL_1.push(new Square(240, 400, 100, 100, "grey", true)); //Top Square
LEVEL_1.push(new Circle(400, 560, 50, "grey", true)); // Right Circle
LEVEL_1.push(new Circle(290, 560, 50, "grey", true)); //Left Circle
LEVEL_1.push(new RightTriangle(460, 400, 100, 100, "grey", 270, true)); // Right - Triangle
LEVEL_1.push(new RightTriangle(130, 440, 100, 100, "grey", 180, true)); // Left - Triangle

shapes.push(...LEVEL_1);

//====================================
//          Progress Bar
//====================================

const progressBar = document.getElementById("progressBar");

// Update the progress bar with a percentage value
function updateProgressBar() {
  percentage = getProgressBarPercentage();
  console.log("Progress - ", percentage);
  progressBar.style.width = percentage + "%";
}

function getProgressBarPercentage() {
  const TOTAL_TILES_IN_LEVEL = LEVEL_1.length; //Change as needed
  let level_tiles_filled = 0;

  for (let targetShape of shapes.filter((s) => s.isLevelShape)) {
    if (targetShape.isLevelShapeFilled) level_tiles_filled += 1;
  }

  console.log(level_tiles_filled, " // ", TOTAL_TILES_IN_LEVEL);

  let percent_level_complete =
    (level_tiles_filled / TOTAL_TILES_IN_LEVEL) * 100;

  return Math.round(percent_level_complete);
}

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
//        Collect mouse data
//====================================
function getTimestamp() {
  // Create a new Date object
  const currentDate = new Date();

  // Get the individual components of the current timestamp
  const hours = currentDate.getHours().toString().padStart(2, "0");
  const minutes = currentDate.getMinutes().toString().padStart(2, "0");
  const seconds = currentDate.getSeconds().toString().padStart(2, "0");
  const milliseconds = currentDate
    .getMilliseconds()
    .toString()
    .padStart(3, "0");

  // Format the timestamp
  const formattedTimestamp = `${hours}:${minutes}:${seconds}:${milliseconds}`;

  return formattedTimestamp;
}

document.ondragover = function (event) {
  mouse_motion_accumulator += 1;

  //Collect mouse data every interval set by global var
  if (mouse_motion_accumulator % mouse_motion_collect_interval != 0) return;

  if (mouse_motion_array.length > 0) {
    console.log("Dragging Img - ", event.clientX, " , ", event.clientY);
    mouse_motion_array.push([event.clientX, event.clientY, getTimestamp()]);
  }
};

function postMouseMotionData() {
  fetch("/process-mouse-data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ data: mouse_motion_array }),
  })
    .then((res) => console.log(res))
    .catch((err) => console.log(err));
}

//====================================
//          Block Options
//====================================
const shapeContainer = document.getElementById("shapeContainer");
const shapeImages = document.querySelectorAll(".building-blocks");

// Prevent the default "no-drop" behavior on the canvas element
canvas.addEventListener("dragover", (event) => {
  event.preventDefault();
});

shapeContainer.addEventListener("mousedown", function (event) {
  if (event.target.tagName === "IMG") {
    draggingImage = {
      image: event.target,
      offsetX: event.offsetX,
      offsetY: event.offsetY,
    };

    mouse_motion_array.push([event.clientX, event.clientY, getTimestamp()]); //Start of mouse motion

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
  //Reset and Post Mouse Motion
  console.log("End of motion - ", mouse_motion_array);
  postMouseMotionData();
  mouse_motion_accumulator = 0;
  mouse_motion_array = [];

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
    } else if (shapeType === "circle") {
      newShape = new Circle(x, y, 50, "red");
    } else if (shapeType === "rightTriangle") {
      newShape = new RightTriangle(
        x - draggingImage.offsetX,
        y - draggingImage.offsetY,
        100,
        100,
        "blue"
      );
    }

    // Add the new shape to the shapes array
    shapes.push(newShape);

    // Redraw the canvas
    drawShapes();

    let shape = shapes[shapes.length - 1];
    for (let targetShape of shapes.filter((s) => s.isLevelShape)) {
      // Check if the shape is close enough to a special shape and snap it if true
      shape.snapToTargetShape(targetShape);
      updateProgressBar();
    }

    drawShapes();
  }

  draggingImage = null;
}

//====================================
//      Controls / EventListeners
//====================================
function mouse_down(event) {
  event.preventDefault();
  // console.log("Mouse down - ", event);
  console.log("Dragging Start Img - ", event.clientX, " , ", event.clientY);

  const { x, y } = calculateMousePos(event);

  // Check if the mouse is inside any shape
  for (let i = shapes.length - 1; i >= 0; i--) {
    const shape = shapes[i];

    //Prevent level tiles & snapped shapes from being moved
    if (shape.isPointInside(x, y) && !shape.isLevelShape && !shape.isSnapped) {
      console.log("Inside of a shape");
      current_shape_index = i;
      shape.mouseDown(x, y);

      // Move the shape to the top of the stack
      // shapes.push(shapes.splice(i, 1)[0]);

      break;
    }
  }
}

function mouse_up(event) {
  console.log("UP");
  event.preventDefault();

  if (current_shape_index === null) return;

  const shape = shapes[current_shape_index];

  shape.mouseUp();
  current_shape_index = null;
}

function mouse_move(event) {
  if (current_shape_index === null) return;

  const shape = shapes[current_shape_index];

  for (let targetShape of shapes.filter((s) => s.isLevelShape)) {
    // Check if the shape is close enough to a special shape and snap it if true
    shape.snapToTargetShape(targetShape);
    updateProgressBar();
  }

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

//Testing

function rotateCurrentShape() {
  if (current_shape_index !== null) {
    const shape = shapes[current_shape_index];
    shape.rotation += 45; // Adjust the rotation angle as desired
    drawShapes();
  }
}

document.addEventListener("keydown", function (event) {
  if (event.key === "r" || event.key === "R") {
    rotateCurrentShape();
    console.log("Rotated shape");
  }
});

drawShapes();
