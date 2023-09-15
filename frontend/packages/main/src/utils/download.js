const BASE_URL = "./api/engine";

function downloadLearnwareSync(id) {
  const url = `${BASE_URL}/download_learnware?learnware_id=${id}`;
  window.open(url);
}

export { downloadLearnwareSync };