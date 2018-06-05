/**
 *
 * js/concerns/concern_detail.js
 *
 */
$(function () {

  /* ノード情報と接続情報を取得する */
  let reg = /\/graph\/concerns\/([^\/]+)\//;
  let concernId = location.href.match(reg)[1];
  let url = `/graph/concerns/${concernId}.json/`;
  $.getJSON(url, (data) => {

    let nodes = data["nodes"];
    let links = data["links"];

    // グラフを描画する
    let svgId = "svgArea";
    let arrowColor = "gray";    // 矢印の色 ( デフォルトで lightgray )
    let distance = 40;    // ノード間の距離 ( デフォルトは 50 )
    let force = new ForceConcern(svgId, nodes, links,
      arrowColor, distance);

  });    // end of $.getJSON(url, ...)

}());