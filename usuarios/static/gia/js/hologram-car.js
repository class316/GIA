(function () {
    function initHologram(container) {
        if (!window.THREE || !THREE.GLTFLoader) {
            container.textContent = 'Holograma no disponible';
            return;
        }

        const modelPath = container.dataset.modelSrc;
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x001722, 0.048);

        const width = container.clientWidth || 520;
        const height = container.clientHeight || 300;
        const camera = new THREE.PerspectiveCamera(58, width / height, 0.1, 1000);
        camera.position.set(0, 2.1, 6.4);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setClearColor(0x000000, 0);
        container.appendChild(renderer.domElement);

        const cyan = new THREE.Color(0x38bdf8);
        const hologramMaterial = new THREE.MeshBasicMaterial({
            color: cyan,
            wireframe: true,
            transparent: true,
            opacity: 0.72,
        });

        scene.add(new THREE.AmbientLight(0x38bdf8, 0.95));

        const grid = new THREE.GridHelper(14, 28, 0x38bdf8, 0x0f3b4a);
        grid.position.y = -1.05;
        scene.add(grid);

        const platform = new THREE.Group();
        scene.add(platform);
        for (let i = 0; i < 4; i += 1) {
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(1.75 + i * 0.38, 0.01, 8, 140),
                new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.38 })
            );
            ring.rotation.x = Math.PI / 2;
            ring.position.y = -0.98;
            platform.add(ring);
        }

        const particleGeometry = new THREE.BufferGeometry();
        const particleCount = 420;
        const positions = new Float32Array(particleCount * 3);
        for (let i = 0; i < particleCount; i += 1) {
            positions[i * 3] = (Math.random() - 0.5) * 11;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 5;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 11;
        }
        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particles = new THREE.Points(
            particleGeometry,
            new THREE.PointsMaterial({ color: 0x38bdf8, size: 0.025, transparent: true, opacity: 0.62 })
        );
        scene.add(particles);

        let car = null;
        let mouseX = 0;
        let mouseY = 0;

        function normalizeModel(model) {
            const box = new THREE.Box3().setFromObject(model);
            const size = new THREE.Vector3();
            const center = new THREE.Vector3();
            box.getSize(size);
            box.getCenter(center);
            model.position.sub(center);
            const maxAxis = Math.max(size.x, size.y, size.z);
            model.scale.setScalar(maxAxis > 0 ? 4.7 / maxAxis : 1);
            model.position.y = -0.58;
        }

        function applyHologram(model) {
            model.traverse(function (child) {
                if (child.isMesh) {
                    child.material = hologramMaterial.clone();
                    child.material.needsUpdate = true;
                }
            });
        }

        function setCar(model) {
            if (car) {
                scene.remove(car);
            }
            car = model;
            applyHologram(car);
            normalizeModel(car);
            scene.add(car);
        }

        function createFallbackCar() {
            const group = new THREE.Group();
            const body = new THREE.Mesh(new THREE.BoxGeometry(4.4, 0.75, 1.7, 14, 4, 8), hologramMaterial.clone());
            group.add(body);
            const cabin = new THREE.Mesh(new THREE.BoxGeometry(2.05, 0.88, 1.35, 12, 5, 8), hologramMaterial.clone());
            cabin.position.set(0.22, 0.78, 0);
            group.add(cabin);
            const wheelGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.22, 40, 4, true);
            const wheelMat = new THREE.MeshBasicMaterial({ color: 0xf97316, wireframe: true, transparent: true, opacity: 0.85 });
            [[-1.45, -0.45, 0.9], [1.45, -0.45, 0.9], [-1.45, -0.45, -0.9], [1.45, -0.45, -0.9]].forEach(function (pos) {
                const wheel = new THREE.Mesh(wheelGeo, wheelMat);
                wheel.rotation.z = Math.PI / 2;
                wheel.position.set(pos[0], pos[1], pos[2]);
                group.add(wheel);
            });
            return group;
        }

        setCar(createFallbackCar());

        new THREE.GLTFLoader().load(
            modelPath,
            function (gltf) {
                setCar(gltf.scene);
            },
            undefined,
            function () {
                setCar(createFallbackCar());
            }
        );

        container.addEventListener('mousemove', function (event) {
            const rect = container.getBoundingClientRect();
            mouseX = ((event.clientX - rect.left) / rect.width - 0.5) * 0.55;
            mouseY = ((event.clientY - rect.top) / rect.height - 0.5) * 0.28;
        });

        const clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();
            if (car) {
                car.rotation.y = Math.sin(t * 0.35) * 0.25 + mouseX;
                car.rotation.x = 0.05 + mouseY;
                car.position.y = -0.58 + Math.sin(t * 1.8) * 0.06;
            }
            camera.lookAt(0, 0, 0);
            platform.rotation.y += 0.008;
            grid.position.z = (t * 0.65) % 1;
            particles.rotation.y += 0.0008;
            hologramMaterial.opacity = 0.62 + Math.sin(t * 7) * 0.08;
            renderer.render(scene, camera);
        }
        animate();

        function resize() {
            const nextWidth = container.clientWidth || width;
            const nextHeight = container.clientHeight || height;
            camera.aspect = nextWidth / nextHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(nextWidth, nextHeight);
        }
        window.addEventListener('resize', resize);
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.gia-three-hologram').forEach(initHologram);
    });
})();
