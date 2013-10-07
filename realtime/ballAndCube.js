// Extended example from https://github.com/mrdoob/three.js/
// http://www.aerotwist.com/tutorials/getting-started-with-three-js/
var camera, scene, renderer;
var geometry, material, mesh;
var direction = 1;

init();
animate();

function init() {
        // set the scene size
    var WIDTH = 400,
	    HEIGHT = 300;

	// set some camera attributes
	var VIEW_ANGLE = 45,
	    ASPECT = WIDTH / HEIGHT,
	    NEAR = 0.1,
	    FAR = 10000;

	// get the DOM element to attach to
	// - assume we've got jQuery to hand
	var $container = $('#container');

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
    camera.position.z = 300;

    scene = new THREE.Scene();

    geometry = new THREE.CubeGeometry(200, 200, 200);
    material = new THREE.MeshBasicMaterial({
        color: 0xff00cc,
        wireframe: true
    });

    mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    console.log(mesh);
    
    geometry = new THREE.SphereGeometry(100, 16, 16);
    material = new THREE.MeshBasicMaterial({
        color: 0xff0000,
//        wireframe: true
    });

    mesh2 = new THREE.Mesh(geometry, material);
    scene.add(mesh2);

    renderer = new THREE.CanvasRenderer();
//    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setSize(400, 300);
    
    // attach the render-supplied DOM element
	$container.append(renderer.domElement);

//    document.body.appendChild(renderer.domElement);

}

function animate() {

    // note: three.js includes requestAnimationFrame shim
    requestAnimationFrame(animate);

    mesh.rotation.x += 0.01;
    mesh.rotation.y += 0.02;

    if(mesh2.position.x > 100) {
        direction = -1;
    }
    if(mesh2.position.x < -100) {
        direction = 1;
    }
    mesh2.position.x += direction * 1;

//    mesh2.position.x += 1;
    renderer.render(scene, camera);

}