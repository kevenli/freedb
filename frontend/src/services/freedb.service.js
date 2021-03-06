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

    deleteCollection(db_name, col_name){
        return http.delete(`/databases/${db_name}/collections/${col_name}`);
    }

    queryCollection(db_name, col_name, query={}, skip=0, sort="", limit=20){
        return http.get(`/databases/${db_name}/collections/${col_name}/documents?query=${JSON.stringify(query)}&skip=${skip}&sort=${sort}&limit=${limit}`)
    }

    saveDoc(db_name, col_name, data){
        return http.post(`/databases/${db_name}/collections/${col_name}/documents`, data);
    }

    uploadDocs(db_name, col_name, file){
        var formData = new FormData();
        formData.append("file", file);
        return http.post(`/databases/${db_name}/collections/${col_name}/documents`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
        })
    }

    importDocs(db_name, col_name, file, id_field='id'){
        var formData = new FormData();
        formData.append("file", file);
        var config = {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
        return http.post(`/databases/${db_name}/collections/${col_name}/documents:import?id_field=` + id_field, 
            formData, config)
    }
}

export default new FreedbDataService();