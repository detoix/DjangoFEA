(function () {
    'use strict';
    angular.module('djangofea', ['ngRoute'])
        .controller('Controller', ['$scope', '$http', '$location', Controller])
        .controller('AuthenticationController', ['$scope', '$http', '$location', AuthenticationController])

    function AuthenticationController($scope, $http, $location) {
        $scope.login = function () {
            $http.post('/auth_api/login/', $scope.user)
                .then(
                function () { $location.url('/'); }, function () { $location.url('/'); });
        };

        $scope.logout = function () {
            $http.get('/auth_api/logout/')
                .then(
                function () { $location.url('/'); });
        };
    }

    function Controller($scope, $http, $location) {
        $scope.nodes = []
        $scope.nodesIds = []
        $http.get('/nodes/').then(function (response) {
            $scope.nodes = response.data;
            $scope.nodesIds = response.data.map(function (v) { return v.id; });
        })

        $scope.sections = []
        $scope.sectionsIds = []
        $http.get('/sections/').then(function (response) {
            $scope.sections = response.data;
            $scope.sectionsIds = response.data.map(function (v) { return v.id; });
        })

        $scope.elements = []
        $scope.elementsIds = []
        $http.get('/elements/').then(function (response) {
            $scope.elements = response.data;
            $scope.elementsIds = response.data.map(function (v) { return v.id; });
        })

        $scope.concentratedLoads = []
        $http.get('/concentrated-loads/').then(function (response) {
            $scope.concentratedLoads = response.data;
        })

        $scope.onload = function () {
            $scope.load('model')
        }

        $scope.deflection = function () {
            $scope.load('deflection')
        }

        $scope.bending = function () {
            $scope.load('bending')
        }

        $scope.shear = function () {
            $scope.load('shear')
        }

        $scope.axial = function () {
            $scope.load('axial')
        }

        $scope.load = function (expected) {
            var modelChart = document.getElementById('model_chart');

            $http.get('/' + expected + '/').then(function (response) {
                var chart = new Chart(modelChart,
                    {
                        type: 'scatter',
                        data: JSON.parse(response.data),
                    })
            }) 
        }

        $scope.add_node = function (nodes) {

            var node = {
                x: $scope.x,
                y: $scope.y,
                project_name: $scope.x,
                author: 1,
                x_boundary_condition: $scope.x_boundary_condition,
                y_boundary_condition: $scope.y_boundary_condition,
                fi_boundary_condition: $scope.fi_boundary_condition
            };

            $http.post('/nodes/', node).then(
                function (response) {
                    nodes.push(response.data);
                },
                function () {
                    alert('Something went wrong');
                }
            );
        };

        $scope.add_section = function (sections) {

            var section = {
                E: $scope.E,
                A: $scope.A,
                project_name: $scope.A,
                author: 1,
                J: $scope.J,
                ro: $scope.ro,
            };

            $http.post('/sections/', section).then(
                function (response) {
                    sections.push(response.data);
                },
                function () {
                    alert('Something went wrong');
                }
            );
        };

        $scope.add_element = function (elements) {

            var element = {
                section: $scope.section,
                node_start: $scope.node_start,
                node_end: $scope.node_end,
                hinge_start: $scope.hinge_start,
                hinge_end: $scope.hinge_end,
                project_name: $scope.hinge_start,
                author: 1,
            };

            $http.post('/elements/', element).then(
                function (response) {
                    elements.push(response.data);
                },
                function () {
                    alert('Something went wrong');
                }
            );
        };
    }

    $scope.add_concentrated_load = function (concentratedLoads) {

        var concentratedLoad = {
            associated_element: $scope.associated_element,
            f1: $scope.f1,
            coord1: $scope.coord1,
            author: 1,
            m: $scope.m,
            deg: $scope.deg,
        };

        $http.post('/concentrated-loads/', concentratedLoad).then(
            function (response) {
                concentratedLoads.push(response.data);
            },
            function () {
                alert('Something went wrong');
            }
        );
    };
}());