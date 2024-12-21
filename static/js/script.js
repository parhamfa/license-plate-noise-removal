$(document).ready(function () {
  let currentTempFilename = null;
  let pipelineSteps = [];

  // 1. Upload
  $("#upload-button").on("click", function () {
    const files = $("#file-input")[0].files;
    if (!files.length) {
      showMessage("No files selected.", "danger");
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files[]", files[i]);
    }
    $.ajax({
      url: "/upload",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (res) {
        if (res.status === "success") {
          showMessage(res.message, "success");
          loadCurrentImage();
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error uploading files.", "danger");
      },
    });
  });

  // 2. Load current image
  function loadCurrentImage() {
    $.ajax({
      url: "/current-image",
      type: "GET",
      success: function (res) {
        if (res.status === "success") {
          const filename = res.filename;
          const currentIndex = res.currentIndex;
          const total = res.totalImages;
          const lastFilter = res.filterName || "None";

          const timestamp = Date.now();
          const imgUrl = `/image/${filename}?v=${timestamp}`;
          $("#image-container").html(`<img src="${imgUrl}" alt="Current Image" />`);

          $("#filter-select").val(lastFilter);

          updateNavButtons(currentIndex, total);

          currentTempFilename = null;
          $("#confirm-button").prop("disabled", true);

          // Hide all single-filter param panels
          hideAllSingleFilterParams();
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Could not load current image.", "danger");
      },
    });
  }

  // 3. Next/Prev
  $("#next-button").on("click", function () {
    $.ajax({
      url: "/next-image",
      type: "POST",
      success: function (res) {
        if (res.status === "success") {
          loadCurrentImage();
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error moving to next image.", "danger");
      },
    });
  });

  $("#prev-button").on("click", function () {
    $.ajax({
      url: "/prev-image",
      type: "POST",
      success: function (res) {
        if (res.status === "success") {
          loadCurrentImage();
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error moving to previous image.", "danger");
      },
    });
  });

  // 4. Single-Filter UI
  $("#filter-select").on("change", function () {
    hideAllSingleFilterParams();
    const val = $(this).val();
    switch (val) {
      case "Manual Threshold":
        $("#param-manual-threshold").show();
        break;
      case "Otsu Threshold":
        $("#param-otsu-threshold").show();
        break;
      case "Adaptive Threshold":
        $("#param-adaptive-threshold").show();
        break;
      case "Non-Local Means":
        $("#param-hStrength").show();
        break;
      case "CLAHE":
        $("#param-clipLimit").show();
        break;
      case "Gamma Correction":
        $("#param-gamma").show();
        break;
      case "Unsharp Mask":
        $("#param-unsharp").show();
        break;
    }
  });

  function hideAllSingleFilterParams() {
    $("#param-manual-threshold").hide();
    $("#param-otsu-threshold").hide();
    $("#param-adaptive-threshold").hide();
    $("#param-hStrength").hide();
    $("#param-clipLimit").hide();
    $("#param-gamma").hide();
    $("#param-unsharp").hide();
  }

  // 5. Single-Filter: Apply
  $("#apply-filter-button").on("click", function () {
    const filterName = $("#filter-select").val();

    const data = { filterName };

    // Gather relevant params
    if ($("#param-manual-threshold").is(":visible")) {
      data.threshold = $("#manual-thr-value").val();
    }
    if ($("#param-adaptive-threshold").is(":visible")) {
      data.blockSize = $("#adaptive-blocksize").val();
      data.C = $("#adaptive-c").val();
    }
    // Otsu has none
    if ($("#param-hStrength").is(":visible")) {
      data.hStrength = $("#hStrength-value").val();
    }
    if ($("#param-clipLimit").is(":visible")) {
      data.clipLimit = $("#clipLimit-value").val();
    }
    if ($("#param-gamma").is(":visible")) {
      data.gamma = $("#gamma-value").val();
    }
    if ($("#param-unsharp").is(":visible")) {
      data.sigma = $("#unsharp-sigma").val();
      data.strength = $("#unsharp-strength").val();
    }

    $.ajax({
      url: "/apply-filter",
      type: "POST",
      data: data,
      success: function (res) {
        if (res.status === "success") {
          currentTempFilename = res.processedFilename;
          const timestamp = Date.now();
          const imgUrl = `/image/${res.processedFilename}?v=${timestamp}`;
          $("#image-container").html(`<img src="${imgUrl}" alt="Processed Image" />`);
          $("#confirm-button").prop("disabled", false);
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error applying filter.", "danger");
      },
    });
  });

  // 6. Multi-Filter Pipeline
  $("#show-pipeline-params").on("click", function () {
    hideAllPipelineParams();
    $("#pipeline-param-panel").show();

    const val = $("#pipeline-filter-select").val();
    switch (val) {
      case "Manual Threshold":
        $("#pipeline-param-manual-thr").show();
        break;
      case "Otsu Threshold":
        $("#pipeline-param-otsu-thr").show();
        break;
      case "Adaptive Threshold":
        $("#pipeline-param-adaptive-thr").show();
        break;
      case "Non-Local Means":
        $("#pipeline-param-hStrength").show();
        break;
      case "CLAHE":
        $("#pipeline-param-clahe").show();
        break;
      case "Gamma Correction":
        $("#pipeline-param-gamma").show();
        break;
      case "Unsharp Mask":
        $("#pipeline-param-unsharp").show();
        break;
      // etc. (Gaussian Blur, etc. don't have params in this example)
    }
  });

  function hideAllPipelineParams() {
    $("#pipeline-param-manual-thr").hide();
    $("#pipeline-param-otsu-thr").hide();
    $("#pipeline-param-adaptive-thr").hide();
    $("#pipeline-param-hStrength").hide();
    $("#pipeline-param-clahe").hide();
    $("#pipeline-param-gamma").hide();
    $("#pipeline-param-unsharp").hide();
  }

  $("#add-filter-step").on("click", function () {
    const filterName = $("#pipeline-filter-select").val();
    let params = {};

    // Gather from whichever panel is visible
    switch (filterName) {
      case "Manual Threshold":
        params.threshold = $("#pipeline-manual-thr").val();
        break;
      case "Otsu Threshold":
        // no params
        break;
      case "Adaptive Threshold":
        params.blockSize = $("#pipeline-adaptive-block").val();
        params.C = $("#pipeline-adaptive-c").val();
        break;
      case "Non-Local Means":
        params.hStrength = $("#pipeline-hStrength-val").val();
        break;
      case "CLAHE":
        params.clipLimit = $("#pipeline-clahe-clip").val();
        break;
      case "Gamma Correction":
        params.gamma = $("#pipeline-gamma-val").val();
        break;
      case "Unsharp Mask":
        params.sigma = $("#pipeline-unsharp-sigma").val();
        params.strength = $("#pipeline-unsharp-strength").val();
        break;
      // etc.
    }

    pipelineSteps.push({ filterName, params });
    renderPipelineSteps();
    $("#pipeline-param-panel").hide();
  });

  function renderPipelineSteps() {
    $("#pipeline-steps").empty();
    pipelineSteps.forEach((step, index) => {
      const stepTxt = `${index + 1}. ${step.filterName} ${JSON.stringify(step.params)}`;
      const li = $(`
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <span>${stepTxt}</span>
          <button class="btn btn-sm btn-danger remove-step" data-index="${index}">Remove</button>
        </li>
      `);
      $("#pipeline-steps").append(li);
    });
  }

  $("#pipeline-steps").on("click", ".remove-step", function () {
    const idx = $(this).data("index");
    pipelineSteps.splice(idx, 1);
    renderPipelineSteps();
  });

  $("#preview-pipeline-button").on("click", function () {
    if (pipelineSteps.length === 0) {
      showMessage("Pipeline is empty. Add at least one step.", "warning");
      return;
    }

    $.ajax({
      url: "/apply-pipeline",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ steps: pipelineSteps }),
      success: function (res) {
        if (res.status === "success") {
          currentTempFilename = res.processedFilename;
          const timestamp = Date.now();
          const imgUrl = `/image/${res.processedFilename}?v=${timestamp}`;
          $("#image-container").html(`<img src="${imgUrl}" alt="Pipeline Result" />`);
          $("#confirm-button").prop("disabled", false);
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error applying pipeline.", "danger");
      },
    });
  });

  // 7. Confirm & Export
  $("#confirm-button").on("click", function () {
    if (!currentTempFilename) {
      showMessage("No processed image to confirm.", "warning");
      return;
    }

    $.ajax({
      url: "/confirm-filter",
      type: "POST",
      data: { tempFilename: currentTempFilename },
      success: function (res) {
        if (res.status === "success") {
          showMessage(res.message, "success");
          $("#confirm-button").prop("disabled", true);
          $("#export-button").prop("disabled", false);
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error confirming filter/pipeline.", "danger");
      },
    });
  });

  $("#export-button").on("click", function () {
    $.ajax({
      url: "/export",
      type: "GET",
      success: function (res) {
        if (res.status === "success") {
          showMessage(res.message, "success");
        } else {
          showMessage(res.message, "danger");
        }
      },
      error: function () {
        showMessage("Error exporting images.", "danger");
      },
    });
  });

  // Utility
  function updateNavButtons(idx, total) {
    if (total <= 1) {
      $("#prev-button").prop("disabled", true);
      $("#next-button").prop("disabled", true);
      return;
    }
    $("#prev-button").prop("disabled", idx === 0);
    $("#next-button").prop("disabled", idx === total - 1);
  }

  function showMessage(msg, type = "info") {
    const alertId = `alert-${Date.now()}`;
    const alertHtml = `
      <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${msg}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    $("#messages").prepend(alertHtml);
    setTimeout(() => {
      $(`#${alertId}`).fadeOut(500, function () {
        $(this).remove();
      });
    }, 10000);
  }
});
