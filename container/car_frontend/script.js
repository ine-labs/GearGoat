const data_dir = "./data";
const DOOR_LOCKED = 0;
const DOOR_UNLOCKED = 1;
const OFF = 0;
const ON = 1;

let canfd_on = 1;
let debug = 0;
let randomize = 0;
let seed = 0;
let current_speed = 0;
let door_status = [0, 0, 0, 0];
let turn_status = [0, 0];

function update_doors() {
  if (door_status.every(door => door === DOOR_LOCKED)) {
    for (let i = 0; i < 4; i++) {
        document.getElementById(`door-${i+1}`).style.backgroundColor = 'red';
      }
    return;
  }

  for (let i = 0; i < 4; i++) {
      if (door_status[i] === DOOR_UNLOCKED) {
          document.getElementById(`door-${i+1}`).style.backgroundColor = 'green';
      }
      else {
        document.getElementById(`door-${i+1}`).style.backgroundColor = 'red';
      }
        
  }
}


function update_turn_signals() {
  if (turn_status[0] === "OFF") {

      document.getElementById('left-indicator').style.backgroundColor = '#aaa';      

  }
  else {

      document.getElementById('left-indicator').style.backgroundColor = 'orange';

  }

  if (turn_status[1] === "OFF") {

      document.getElementById('right-indicator').style.backgroundColor = '#aaa';

  } 
  else {

      document.getElementById('right-indicator').style.backgroundColor = 'orange';

  }
}


function update_speed() {
  document.getElementById('current-speed').textContent = current_speed.toFixed(2).padStart(5, '0');
  
}

var socket = io.connect('http://localhost:3050');
console.log('Simulator Server Started...');

// Listen for events from the simulator server
socket.on('car_state', function(data) {
  if ("turn_status" in data) {
    turn_status = data["turn_status"];
    update_turn_signals();
} else if ("door_status" in data) {
    door_status = data["door_status"];
    update_doors();
} else if ("current_speed" in data) {
    current_speed = data["current_speed"];
    update_speed();
}
});


//Controller Socket

var socket2 = io.connect('http://localhost:3500');

socket2.on('connect', function() {
    console.log('Controller WebSocket connection opened.');
});

// Handle connection closed
socket2.on('disconnect', function() {
    console.log('Controller WebSocket connection closed.');
});

// Handle errors
socket2.on('error', function(error) {
    console.error('Controller WebSocket error:', error);
});

// Handle button click to send a message
document.getElementById("leftindicator").addEventListener("mousedown", function() {
  socket2.emit('canframe', {'turning':-1});
  console.log('left indicator clicked.');
});

document.getElementById("leftindicator").addEventListener("mouseup", function() {
  console.log('left indicator released.');
  socket2.emit('canframe', {'turning':0});
});

document.getElementById("rightindicator").addEventListener("mousedown", function() {
  console.log('right indicator clicked.');
  socket2.emit('canframe', {'turning':1});
});

document.getElementById("rightindicator").addEventListener("mouseup", function() {
  console.log('right indicator released.');
  socket2.emit('canframe', {'turning':0});
});

document.getElementById("door1unlock").addEventListener("mousedown", function() {
  console.log('door 1 unlocked.');
  socket2.emit('canframe', {'unlockdoor': '1st'});
});

document.getElementById("door1lock").addEventListener("mousedown", function() {
  console.log('door 1 locked.');
  socket2.emit('canframe', {'lockdoor': '1st'});
});

document.getElementById("door2unlock").addEventListener("mousedown", function() {
  console.log('door 2 unlocked.');
  socket2.emit('canframe', {'unlockdoor': '2nd'});
});

document.getElementById("door2lock").addEventListener("mousedown", function() {
  console.log('door 2 locked.');
  socket2.emit('canframe', {'lockdoor': '2nd'});
});

document.getElementById("door3unlock").addEventListener("mousedown", function() {
  console.log('door 3 unlocked.');
  socket2.emit('canframe', {'unlockdoor': '3rd'});
});

document.getElementById("door3lock").addEventListener("mousedown", function() {
  console.log('door 3 locked.');
  socket2.emit('canframe', {'lockdoor': '3rd'});
});

document.getElementById("door4unlock").addEventListener("mousedown", function() {
  console.log('door 4 unlocked.');
  socket2.emit('canframe', {'unlockdoor': '4th'});
});

document.getElementById("door4lock").addEventListener("mousedown", function() {
  console.log('door 4 locked.');
  socket2.emit('canframe', {'lockdoor': '4th'});
});

document.getElementById("accelerate").addEventListener("mousedown", function() {
  console.log('accelerated');
  socket2.emit('canframe', {'throttle': 1});
});

document.getElementById("accelerate").addEventListener("mouseup", function() {
  console.log('deccelerated');
  socket2.emit('canframe', {'throttle': -1});
});
