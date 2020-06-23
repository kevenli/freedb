import http from "../http-common";
import Cookies from 'js-cookie';

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

    queryCollection(db_name, col_name, query={}, skip=0, sort="", limit=20){
        return http.get(`/databases/${db_name}/collections/${col_name}?query=${JSON.stringify(query)}&skip=${skip}&sort=${sort}&limit=${limit}`)
    }

    saveDoc(db_name, col_name, data){
        return http.post(`/databases/${db_name}/collections/${col_name}/documents`, data);
    }
}

export default new FreedbDataService();