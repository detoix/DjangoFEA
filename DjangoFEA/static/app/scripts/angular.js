(function () {
    'use strict';
    angular.module('djangofea', ['ngRoute', 'rzModule'])
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
        $http.get('/nodes/').then(function (response) {
            $scope.nodes = response.data;
        })

        $scope.sections = []
        $http.get('/sections/').then(function (response) {
            $scope.sections = response.data;
        })

        $scope.elements = []
        $http.get('/elements/').then(function (response) {
            $scope.elements = response.data;
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

        $scope.slider = {
            value: 5,
            options: {
                floor: 0,
                ceil: 10,
                step: 0.1,
                precision: 1,
                hidePointerLabels: true,
                hideLimitLabels: true,
            }
        };

        $scope.$on("slideEnded", function () {
            $scope.load($scope.current)
        });

        $scope.load = function (expected) {
            $scope.current = expected;
            var scale = $scope.slider.value;
            var modelChart = document.getElementById('model_chart');
            $http.get('/' + expected + '/').then(function (response) {
                var data = JSON.parse(response.data);
                data.datasets.forEach(function (dataset) {
                    dataset.data.forEach(function (point) {
                        if (point.tag) {
                            point.x = point.x0 + scale * (point.dx * point.cos - point.dy * point.sin);
                            point.y = point.y0 + scale * (point.dx * point.sin + point.dy * point.cos);
                        }
                    });
                });

                if (!!$scope.chart) {
                    $scope.chart.destroy();
                }

                $scope.chart = new Chart(modelChart, {
                    type: 'scatter',
                    data: data,
                    options: {
                        tooltips: {
                            mode: 'nearest',
                            callbacks: {
                                label: function (tooltipItem, data) {
                                    var value = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                                    if (!value.tag) {
                                        return '(' + value.x + ', ' + value.y + ')';
                                    }
                                    else {
                                        return value.tag;
                                    }
                                }
                            }
                        },
                        animation: {
                            duration: 0
                        },
                        //scales: {
                        //    xAxes: [{
                        //        ticks: {
                        //            stepSize: 1
                        //            //min: 0,
                        //            //max: 3,
                        //        }
                        //    }],
                        //    yAxes: [{
                        //        ticks: {
                        //            stepSize: 1
                        //            //min: 0,
                        //            //max: 1.5,
                        //        }
                        //    }]
                        //}
                    }
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
    }
}());