/**
 *
 * force-concern.js
 *
 */
class ForceConcern extends Force {

  /* 矢印を定義する ( 定義を追加する ) */
  appendArrowHead() {
    super.appendArrowHead();
    
    // 矢印の先端部分の定義を追加する
    // ( node_type = REVERSE の場合 )
    let arrowIdReverse = "arrowHeadReverse";
    this.arrowIdReverse = arrowIdReverse;
    this.defineArrowHead(arrowIdReverse, "crimson");
  }

  /* リンク ( 矢印の色 ) を設定する */
  setLineColor(link) {
    if (link.node_type === 0) return this.arrowColor;
    else return "crimson";
  }

  /* 矢印の先端部分を定義する ( id を指定する ) */
  setArrowHead(link) {
    if (link.node_type === 0) {
      return `url(#${this.arrowId})`;
    } else if (link.node_type === 1) {
      return `url(#${this.arrowIdReverse})`;
    }
  }

  /* ラベルをセットする */
  setLabel(node) {
    return node.content;
  }

  /* ラベルを追加する */
  appendLabels() {
    let labels = super.appendLabels();

    // 薄い/濃い
    let lightOpacity = 0.4;
    let darkOpacity = 1.0;

    // 透明度を指定する
    labels
      .attr("opacity", lightOpacity);

    // ホーバー時にのみ濃く表示する
    labels
      .on("mouseover", function (e) {
        d3.select(this)
          .attr("opacity", darkOpacity);
      })
      .on("mouseout", function (e) {
        d3.select(this)
          .attr("opacity", lightOpacity);
      });

    return labels;
  }

  /* ノードの色を設定する */
  setNodeColor(node) {
    if (node.is_root) return "orange";
    else if (node.node_type === 1) return "crimson";
    else return "teal";
  }

  /* ノードの円 ( circle要素 ) を追加する */
  appendNodeCircles() {
    let circles = super.appendNodeCircles();

    // Concern の ID
    let concernId =
      document.getElementById("id_concern").value;

    // ツールチップ用のクラスを設定する
    circles
      .attr("data-toggle", "tooltip")
      .attr("title", (d) => {

        // Concern の URL
        let baseUrl = `/graph/concerns/${concernId}/`;

        // ノードの編集用の URL
        let nodeEditUrl = `${baseUrl}nodes/edit/${d.nid}/`;

        // 「ノードに接続する」 URL
        let newSourceUrl;
        if (d.is_root) {
          newSourceUrl = `${baseUrl}nodes/new_to_root/`;
        } else {
          newSourceUrl = `${baseUrl}nodes/${d.nid}/new_source/`;
        }

        // 「ノードから接続する」 URL
        let newTargetUrl = `${baseUrl}nodes/${d.nid}/new_target/`;

        // 「このノードを編集する」
        let nodeEdit = `
          <li class="list-group-item">
            <a href="#" to="${nodeEditUrl}">このノードを編集する</a>
          </li>
        `;

        // 「このノードに接続する」
        let sourceNew = `
          <li class="list-group-item">
            <a href="#" to="${newSourceUrl}">このノードに接続する</a>
          </li>
        `;

        // 「接続先のノードを追加」
        let targetNew = `
          <li class="list-group-item">
            <a href="#" to="${newTargetUrl}">接続先のノードを追加</a>
          </li>
        `;

        // ルートがクリックされた場合は 「編集する」 リンクを表示しない
        if (d.is_root) {
          return `
            <ul class="list-group">
              ${sourceNew}
            </ul>
          `;
        } else {
          // ルート以外の場合は全てのリンクを表示する

          return `
            <ul class="list-group">
              ${nodeEdit}
              ${sourceNew}
              ${targetNew}
            </ul>
          `;
        }
      });

    // ツールチップの表示領域
    let tooltipTemplate = `
      <div class="tooltip" role="tooltip">
        <div class="arrow"></div>
        <div class="tooltip-inner" style="background-color:white;"></div>
      </div>
    `;

    // ツールチップを設定する
    let cs = $("g.nodes circle");
    cs.tooltip({
      trigger: "click",
      html: true,
      template: tooltipTemplate,
      animation: true,
    });

    // クリック時にドラッグイベントが発生する
    // (→シミュレーションが restart() される ) のを防ぐ
    circles.on("click", (e) => {
      this.sim.stop();

      // ツールチップに表示されるリンク
      let ttpAnchors = $(".tooltip .tooltip-inner a[to]");
      ttpAnchors.on("click", (ee) => {

        // ツールチップを閉じる
        cs.tooltip("hide");

        // to 属性の URL にリクエスト → モーダルダイアログとして表示する
        let to = $(ee.target).attr("to");
        $.get(to, (data) => {
          $(".modal-body").html(data);
          $("#mdddl").modal();
        });

      });    // end of ttpAnchors.on("click", ...)

    });    // end of circles.on("click", ...)

    return circles;
  }

}