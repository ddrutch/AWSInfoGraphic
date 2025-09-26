document.addEventListener('DOMContentLoaded', ()=>{
  const analyzeBtn = document.getElementById('analyze');
  const fullPipelineBtn = document.getElementById('fullPipeline');
  const sampleBtn = document.getElementById('sample');
  const clearBtn = document.getElementById('clear');

  const contentEl = document.getElementById('content');
  const demoEl = document.getElementById('demo');

  const statusEl = document.getElementById('status');
  const resultArea = document.getElementById('result-area');

  function setBusy(on){
    analyzeBtn.disabled = on;
    fullPipelineBtn.disabled = on;
    sampleBtn.disabled = on;
    clearBtn.disabled = on;

    analyzeBtn.textContent = on ? 'Analyzing...' : 'Analyze Content';
    fullPipelineBtn.innerHTML = on ? '<span class="spinner"></span> Processing...' : '🚀 Full Pipeline';

    statusEl.className = on ? 'demo-status processing' : 'demo-status idle';
    if (on) {
      statusEl.innerHTML = '<span class="spinner"></span> Processing your content...';
    } else {
      statusEl.innerHTML = '<span>Ready to analyze your content</span>';
    }
  }

  function renderNoResults(){
    resultArea.innerHTML = `
      <div class="result-placeholder">
        <div style="font-size: 3rem; margin-bottom: 16px;">🎨</div>
        <div style="font-size: 1.1rem; color: #6b7280; margin-bottom: 8px;">Your infographic outline will appear here</div>
        <div style="color: #9ca3af;">Click "Analyze Content" or "Full Pipeline" to get started!</div>
      </div>
    `;
  }

  function renderResults(data, isFullPipeline = false) {
    const analysis = data.analysis || {};
    const contentAnalysis = data.content_analysis || analysis;
    const imageAssets = data.image_assets || data.images || [];
    const layoutSpec = data.layout_spec || data.layout || {};
    const finalInfographic = data.final_infographic || {};

    let html = '';

    // Title
    const title = contentAnalysis.suggested_title || contentAnalysis.main_topic || 'Generated Infographic';
    html += `<div class="result-title">${title}</div>`;

    // Subtitle with metadata
    let subtitle = '';
    if (isFullPipeline) {
      subtitle = `Layout: ${layoutSpec.layout_type || 'optimized'} | Images: ${imageAssets.length}`;
    }
    if (contentAnalysis.content_type) {
      subtitle += (subtitle ? ' | ' : '') + `Type: ${contentAnalysis.content_type}`;
    }
    if (subtitle) {
      html += `<div class="result-subtitle">${subtitle}</div>`;
    }

    // Show final infographic if available
    if (isFullPipeline && finalInfographic.image_url) {
      html += `
        <div class="final-infographic">
          <div class="infographic-preview">
            <img src="${finalInfographic.image_url}" alt="Generated Infographic" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
          </div>
          <div class="infographic-meta">
            <div class="meta-item">
              <strong>🎨 Final Image:</strong> <a href="${finalInfographic.image_url}" target="_blank">View Full Size</a>
            </div>
            <div class="meta-item">
              <strong>📐 Composition ID:</strong> ${finalInfographic.composition_id || 'Generated'}
            </div>
            <div class="meta-item">
              <strong>📱 Platform:</strong> ${finalInfographic.platform || 'General'}
            </div>
            ${finalInfographic.metadata ? `
              <div class="meta-item">
                <strong>📊 Stats:</strong> ${finalInfographic.metadata.canvas_size ? finalInfographic.metadata.canvas_size.join('x') : 'Auto'} canvas,
                ${finalInfographic.metadata.text_elements || 0} text elements,
                ${finalInfographic.metadata.image_elements || 0} images
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    // Key points
    const keyPoints = contentAnalysis.key_points || [];
    if (keyPoints.length > 0) {
      html += '<div class="result-points">';
      keyPoints.slice(0, 6).forEach((point, index) => {
        html += `
          <div class="result-point">
            <div class="result-point-number">${index + 1}</div>
            <div class="result-point-text">${point}</div>
          </div>
        `;
      });
      html += '</div>';
    }

    // Layout and image info for full pipeline
    if (isFullPipeline && (layoutSpec.layout_type || imageAssets.length > 0)) {
      html += `
        <div class="result-meta">
          <strong>🎨 Layout:</strong> ${layoutSpec.layout_type || 'grid'} |
          <strong>🖼️ Images:</strong> ${imageAssets.length} generated |
          <strong>📐 Sections:</strong> ${layoutSpec.sections ? layoutSpec.sections.length : 'optimized'}
        </div>
      `;
    }

    // Recommendations
    const recommendations = contentAnalysis.recommendations || [];
    if (recommendations.length > 0) {
      html += '<div style="margin-top: 24px; padding: 16px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6;">';
      html += '<strong style="color: #1e40af;">💡 Pro Tips:</strong><br>';
      recommendations.forEach(rec => {
        html += `• ${rec}<br>`;
      });
      html += '</div>';
    }

    resultArea.innerHTML = html;
  }

  async function analyze(){
    const text = contentEl.value.trim();
    if(!text){
      statusEl.innerHTML = '<span style="color: #ef4444;">Please paste some content first.</span>';
      return;
    }
    setBusy(true);

    try{
      const res = await fetch('/api/analyze', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          content:text,
          platform:'general',
          demo:demoEl.checked
        })
      });
      const json = await res.json();
      setBusy(false);

      if(!json.success){
        statusEl.innerHTML = `<span style="color: #ef4444;">Analysis failed: ${json.error||'unknown error'}</span>`;
        return;
      }

      renderResults(json, false);
      statusEl.innerHTML = '<span style="color: #10b981;">✓ Analysis complete! Ready to create your infographic.</span>';

    }catch(err){
      setBusy(false);
      statusEl.innerHTML = `<span style="color: #ef4444;">Request error: ${String(err)}</span>`;
    }
  }

  async function fullPipeline(){
    const text = contentEl.value.trim();
    if(!text){
      statusEl.innerHTML = '<span style="color: #ef4444;">Please paste some content first.</span>';
      return;
    }
    setBusy(true);

    try{
      const res = await fetch('/api/full_analyze', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          content:text,
          platform:'general',
          demo:demoEl.checked
        })
      });
      const json = await res.json();
      setBusy(false);

      if(!json.success){
        statusEl.innerHTML = `<span style="color: #ef4444;">Pipeline failed: ${json.error||'unknown error'}</span>`;
        return;
      }

      renderResults(json, true);
      statusEl.innerHTML = '<span style="color: #10b981;">✓ Full pipeline complete! Your infographic is ready.</span>';

    }catch(err){
      setBusy(false);
      statusEl.innerHTML = `<span style="color: #ef4444;">Request error: ${String(err)}</span>`;
    }
  }

  analyzeBtn.addEventListener('click', analyze);
  fullPipelineBtn.addEventListener('click', fullPipeline);
  sampleBtn.addEventListener('click', ()=>{
    contentEl.value = `How to accelerate cloud migrations:
1. Assess your current workloads and dependencies
2. Prioritize critical applications for early migration
3. Automate deployment pipelines with CI/CD
4. Implement infrastructure as code practices
5. Train teams on cloud-native technologies
6. Monitor performance and optimize costs continuously

Benefits of serverless computing:
- Reduced operational overhead
- Automatic scaling based on demand
- Pay-for-usage pricing model
- Faster time-to-market for new features
- Built-in high availability and fault tolerance`;
  });
  clearBtn.addEventListener('click', ()=>{
    contentEl.value = '';
    renderNoResults();
  });

  // Initialize
  renderNoResults();
});