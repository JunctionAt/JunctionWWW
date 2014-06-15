(function(){
    var notifications = angular.module('notificationsModule', []);

    notifications.service('notifications', ['$rootScope', '$http', function($rootScope, $http) {
        var _service = this;

        this.MARK_READ = "read";

        this.notificationCount = server_page_state["notifications_num"];

        this.ongoingMarks = {};

        // Since this is a PUT operation, we can be certain that as long as we are sending the same request, it won't matter
        // how many times we send it. Therefore, if multiple requests are run for the same data at the same time, we can
        // use one request to answer all callbacks. This should be done automatically by the angular.js $http service.
        this.mark = function (mark, id, success, error) {
            $http.put("/notifications/mark/" + id + "/" + mark)
                .success(function(data, status, headers, config) {
                    // Update and broadcast the new unread notifications count
                    _service.notificationCount = data['notification_count'];
                    $rootScope.$broadcast('notifications:change', _service);

                    if(typeof success == 'function') {
                        success(data, status, headers, config);
                    }
                })
                .error(function(data, status, headers, config) {
                    if(typeof error == 'function') {
                        error(data, status, headers, config);
                    }
                });
        };
    }]);

    // Notifications status
    notifications.controller('notificationsStatus', ['$scope', '$element', 'notifications', function($scope, $element, notifications) {
        $scope.notificationCount = notifications.notificationCount;

        $scope.$on('notifications:change', function(event, data) {
            $scope.notificationCount = data.notificationCount;
        })
    }]);

    notifications.controller('notificationEntry', ['$scope', '$element', 'notifications', function($scope, $element, notifications) {
        $scope.id = $element.data('id');
        $scope.read = $element.hasClass("read");

        $scope.loading = false;

        $scope.markRead = function () {
            $scope.loading = true;
            notifications.mark(notifications.MARK_READ, $scope.id, function() {
                $scope.read = true;
                $scope.loading = false;
            }, function () {
                $scope.loading = false;
            })
        };
    }]);
})();

(function() {
    var bans = angular.module('bansModule', []);

    bans.controller('banInstancePage', ['$scope', function($scope) {
        $scope.ban = $scope.pageState.ban
    }]);

    bans.controller('banWatchControls', ['$scope', '$http', function($scope, $http) {
        $scope.setWatching = function(state) {
            $http.put("/api/anathema/ban/" + $scope.ban.id + "/watch", {
                watch: state ? "True" : "False"
            }).success(function(data, status, headers, config) {
                console.log(data);
                $scope.ban.watching = data.watching;
            })
        }
    }]);
})();

(function(){
    var junctionApp = angular.module('junctionApp', ['notificationsModule', 'bansModule']);

    junctionApp.run(['$rootScope', function($rootScope) {
        $rootScope.pageState = server_page_state;
    }]);

    junctionApp.config(['$httpProvider', function($httpProvider) {
        $httpProvider.interceptors.push(function() {
            return {
                'request': function(config) {
                    config.headers.CSRF = server_page_state.csrf_token;
                    return config;
                }
            }
        })
    }]);
})();