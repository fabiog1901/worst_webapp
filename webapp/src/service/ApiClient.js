import axios from 'axios';

export default class ApiClient {
    getAccountSummary() {
        return axios
            .get('http://localhost:8000/accounts', {
                params: {
                    hh: 12345
                }
            })
            .then((response) => response.data)
            .catch(function (error) {
                console.log(error);
            })
            .finally(function () {
                // always executed
            });
    }
}
