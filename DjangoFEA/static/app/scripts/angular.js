(function () {
    'use strict';
    angular.module('djangofea', [])
        .controller('Controller', ['$scope', '$http', Controller]);

    

    function Controller($scope, $http) {

        $scope.nodes = []
        $http.get('/nodes/').then(function (response) {
            $scope.nodes = response.data;
        })

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
    }
}());