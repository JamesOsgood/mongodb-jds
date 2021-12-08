exports = async function(changeEvent) {

    // Get inserted doc
    var batch_doc = changeEvent.fullDocument

    // Access a mongodb service:
    const bcodes_coll = context.services.get("stock-service-atlas").db("stock").collection("brstck_bcodes");
    const progress_coll = context.services.get("stock-service-atlas").db("stock").collection("batch_progress");
    
    const bcodes = await bcodes_coll.find({'batch_index' : batch_doc.batch_index}).toArray();
    
    const axios = require('axios');
    const config = { headers: { 'content-type': 'application/json' }};
    const response = await axios.post('https://64bc8cfd-2263-488c-b76a-75c230ebbb0f.mock.pstmn.io/JDS_Test', JSON.stringify(bcodes), config);
    console.log(JSON.stringify(response.data));

    return progress_coll.updateOne({}, { $inc : { 'batches_done' : 1, 'bcodes_inserted' : bcodes.length}});
};
