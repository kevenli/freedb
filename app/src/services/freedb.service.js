import http from "../http-common";

class FreedbDataService {
    getAllDb(){
        return http.get('/databases');
    }

    getDb(id){
        return http.get(`/databases/${id}`);
    }

    createDb(data){
        return http.post('/databases', data);
    }

    deleteDb(name){
        return http.delete(`/databases/${name}`);
    }

    createCollection(db_name, data){
        return http.post(`/databases/${db_name}/collections`, data);
    }
}

export default new FreedbDataService();