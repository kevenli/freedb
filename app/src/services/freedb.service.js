import http from "../http-common";

class FreedbDataService {
    getAllDb(){
        return http.get('/databases');
    }

    getDb(id){
        return http.get('/databases/${id}');
    }

    createDb(data){
        return http.post('/databases', data);
    }
}

export default new FreedbDataService();