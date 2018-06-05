/**
 *
 * force.js ( 力学グラフを描画する )
 *
 */
class Force {

  /* コンストラクタ */
  constructor(svgId, nodes, links, 
    arrowColor="lightgray", distance=50) {

    // 引数の処理
    this.nodes = nodes;                   // ノード情報
    this.links = links;                       // ノードの接続情報
    this.arrowColor = arrowColor;    // 矢印の色 ( 接続部分 )
    this.distance = distance;            // ノードの間隔

    // SVG 要素を取得 & サイズを取得
    let svg = d3.select(`#${svgId}`)
    this.svg = svg;
    this.width = svg.style("width").replace("px", "");
    this.height = svg.style("height").replace("px", "");

    // フォースレイアウトの設定
    this.sim = this.setForceSimulation();

    // 矢印を定義する
    this.defs = this.svg.append("defs");
    this.arrowId = "arrowHead";
    this.defineArrowHead(this.arrowId, this.arrowColor);

    // リンク (g要素 + line要素) を追加する
    this.linkGroup = this.appendLinkGroup();

    // ノード (g要素) を追加する
    this.nodeGroup = this.appendNodeGroup();

    // ノードの円を追加する
    // リンクと異なり、g 要素と circle 要素をそれぞれ個別に
    // 取得しているのは、フォースレイアウトによる座標指定は
    // g 要素ごと行う一方で、circle 要素のみにドラッグイベントを
    // 設定するようにしているため
    this.circles = this.appendNodeCircles();

    // tickイベント時の処理を登録する
    this.sim.nodes(nodes).on("tick", () => {
      this.onTick(this.linkGroup, this.nodeGroup);
    });

    // リンクのシミュレーションを開始する
    this.sim.force("link").links(links);

    // ラベルを表示する
    this.labels = this.appendLabels();

    // ドラッグイベントを設定する
    this.setDragEventHandlers();

  }

  /* フォースレイアウトを設定する */
  setForceSimulation() {

    // シミュレーションを開始する &
    // 座標更新用の関数 ( force ) を指定する
    // 以下の "link", "charge", "center" は force の名前
    let sim = d3.forceSimulation(this.nodes)
      .force(
        "link",
        d3.forceLink().id(d => d.id)
          .distance(this.distance)
          .strength(1.5)
      )
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(
        this.width / 2,    // グラフの中心となる位置 ( 横 )
        this.height / 2    // グラフの中心となる位置 ( 縦 )
      ));

    // フォースレイアウトの力学的なパラメータ群
    sim.force("charge")
      .strength(-100);    // クーロン力 (反発力)
    sim.velocityDecay(0.2);    // 摩擦力

    // 2 秒後にシミュレーションを停止させる
    let ms = 2000;
    this.stopAfter(ms);

    return sim;
  }

  /* n ミリ秒後にシミュレーションを停止させる */
  stopAfter(ms) {
    setTimeout(() => { this.sim.stop(); }, ms);
  }

  /* リンク ( g 要素 + line 要素 ) を追加する */
  appendLinkGroup() {

    let linkGroup = this.svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(this.links)
      .enter()
      .append("line")
      .attr("stroke", (link) => this.arrowColor)
      .attr("stroke-width", 1)
      .attr("fill", "none")
      .attr("marker-end", `url(#${this.arrowId})`);

    return linkGroup;
  }

  /* ノード (g要素) を追加する */
  appendNodeGroup() {

    let nodeGroup = this.svg.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(this.nodes)
      .enter()
      .append("g");

    return nodeGroup;
  }

  /* ノードの色を設定する */
  setNodeColor(node) { return "orange"; }

  /* ノードの円 (circle要素) を追加する */
  appendNodeCircles() {

    let circles = this.nodeGroup.append("circle")
      .attr("r", 5)
      .attr("fill", "white")
      .attr("stroke", this.setNodeColor)
      .attr("stroke-width", 3.0);

    return circles;
  }

  /* ラベル ( text 要素 ) の値をセットする */
  setLabel(d) { return d.name; }

  /* ラベルを表示する (text要素を追加する) */
  appendLabels() {

    let labels = this.nodeGroup.append("text")
     .text(this.setLabel)
     .attr("x", 8)
     .attr("y", 3)
     .style("font-size", "11px")
     .style("color", "gray");

    return labels;
  }

  /* tick イベント時の処理 */
  onTick(linkGroup, nodeGroup) {

    // リンクの位置を設定する
    linkGroup
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    // ノードの位置を設定する
    nodeGroup
      .attr("transform", (d) => {
        return `translate(${d.x},${d.y})`;
      });

  }

  /* 矢印を定義する */
  defineArrowHead(arrowId, arrowColor) {
    
    // マーカーを追加
    var marker = this.defs.append("marker")
      .attr("id", arrowId)
      .attr("refX", 13)
      .attr("refY", 0)
      .attr("viewBox", "0 -5 10 10")
      .attr("markerWidth", 13)
      .attr("markerHeight", 13)
      .attr("orient", "auto")
      .attr("xoverflow", "visible");

    // 矢印の先端の部分を追加する
    // M..初期位置
    // V..垂直線を引く?
    // L..直線を引く
    // Z..閉じる
    marker.append("path")
      .attr("d", "M0,-4 L8,0 L0,4")
      .attr("fill", arrowColor)
      .style("stroke", "none");

  };

  /* ドラッグ開始時の処理 */
  onDragStart(node) {
    if (!d3.event.active) {
      this.sim.alphaTarget(0.3).restart();

      // 2 秒後にシミュレーションを停止させる
      this.stopAfter(2000);
    }
    node.fx = node.x;
    node.fy = node.y;
  }

  /* ドラッグ中の処理 */
  onDrag(node) {
    node.fx = d3.event.x;
    node.fy = d3.event.y;
  };

  /* ドラッグ終了時の処理 */
  onDragEnd(node) {
    if (d3.event.active) {
      this.sim.alphaTarget(0);
    }
    node.fx = null;
    node.fy = null;
  };

  /* ドラッグイベントを設定する */
  setDragEventHandlers() {

    this.circles.call(
      d3.drag()
        .on("start", node => this.onDragStart(node))
        .on("drag", this.onDrag)
        .on("end", node => this.onDragEnd(node))
    );

  }

}