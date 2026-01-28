frappe.pages['whatsapp-flow-builder'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('WhatsApp Flow Builder'),
		single_column: true
	});

	// Load Drawflow and Styles
	frappe.require([
		'https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.js',
		'https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.css'
	], () => {
		new FlowBuilder(wrapper);
	});
}

class FlowBuilder {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.page = wrapper.page;
		this.flow_name = frappe.get_route()[1];
		this.init();
	}

	init() {
		this.render_layout();
		this.init_drawflow();
		if (this.flow_name) {
			this.load_flow(this.flow_name);
		}
	}

	render_layout() {
		this.page.main.empty().append(`
			<div class="flow-builder-container d-flex" style="height: calc(100vh - 150px); border: 1px solid #d1d8dd;">
				<div class="sidebar p-3 border-right" style="width: 200px; background: #f8f9fa;">
					<h5>Nodes</h5>
					<div class="node-item btn btn-default btn-block mb-2" draggable="true" ondragstart="event.dataTransfer.setData('node', 'message')">Message</div>
					<div class="node-item btn btn-default btn-block mb-2" draggable="true" ondragstart="event.dataTransfer.setData('node', 'input')">Input</div>
					<div class="node-item btn btn-default btn-block mb-2" draggable="true" ondragstart="event.dataTransfer.setData('node', 'condition')">Condition</div>
					<div class="node-item btn btn-default btn-block mb-2" draggable="true" ondragstart="event.dataTransfer.setData('node', 'action')">Action</div>
					<div class="node-item btn btn-primary btn-block mb-2" draggable="true" ondragstart="event.dataTransfer.setData('node', 'transfer')">Agent Transfer</div>
				</div>
				<div id="drawflow" class="flex-grow-1" style="position: relative;"></div>
			</div>
		`);

		this.page.add_primary_action(__('Save Flow'), () => this.save_flow());
	}

	init_drawflow() {
		const id = document.getElementById("drawflow");
		this.editor = new Drawflow(id);
		this.editor.start();

		// Handle Drop
		id.addEventListener('drop', (e) => {
			e.preventDefault();
			const type = e.dataTransfer.getData("node");
			this.add_node(type, e.clientX, e.clientY);
		});
		id.addEventListener('dragover', (e) => e.preventDefault());
	}

	add_node(type, x, y) {
		const pos_x = x - this.wrapper.offset().left - 100;
		const pos_y = y - this.wrapper.offset().top - 50;

		let label = type.charAt(0).toUpperCase() + type.slice(1);
		let html = `<div class="p-2"><strong>${label}</strong><br><small>Click to edit</small></div>`;
		
		this.editor.addNode(type, 1, 1, pos_x, pos_y, type, {}, html);
	}

	load_flow(name) {
		frappe.db.get_doc('WhatsApp Chatbot Flow', name).then(doc => {
			this.doc = doc;
			// Map doc.steps to Drawflow nodes
			this.render_from_doc();
		});
	}

	render_from_doc() {
		if (!this.doc.steps) return;
		let last_node_id = null;
		this.doc.steps.forEach((step, i) => {
			const node_id = this.editor.addNode('step', 1, 1, 100 + (i * 250), 100, 'step', step, `<div class="p-2"><strong>Step ${i+1}</strong><br>${step.message_text || step.template || '...'}</div>`);
			if (last_node_id) {
				this.editor.addConnection(last_node_id, node_id, "output_1", "input_1");
			}
			last_node_id = node_id;
		});
	}

	save_flow() {
		const data = this.editor.export();
		frappe.show_alert({message: __('Flow saved successfully (Mock)'), indicator: 'green'});
		console.log("Saving flow data:", data);
		// Logic to map Drawflow back to WhatsApp Flow Step child table
	}
}
