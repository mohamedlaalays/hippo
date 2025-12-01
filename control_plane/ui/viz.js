// Scheduler Visualization Handler
class SchedulerVisualizer {
    constructor() {
        this.schedule = null;
        this.setupEventListeners();
        this.tryLoadDefaultFile();
    }

    setupEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const modal = document.getElementById('modal');
        const closeBtn = document.querySelector('.close');

        fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        closeBtn.addEventListener('click', () => modal.style.display = 'none');
        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.style.display = 'none';
        });
    }

    async tryLoadDefaultFile() {
        try {
            // Try to load from the outputs directory
            const response = await fetch('../outputs/schedule_20251201_102202.csv');
            if (response.ok) {
                const text = await response.text();
                this.loadCSV(text);
                document.getElementById('fileName').textContent = 'schedule_20251201_102202.csv (auto-loaded)';
            }
        } catch (e) {
            // Silently fail - user will load manually
        }
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const filename = file.name.toLowerCase();

            if (filename.endsWith('.json')) {
                this.loadJSON(content);
            } else if (filename.endsWith('.csv')) {
                this.loadCSV(content);
            }

            document.getElementById('fileName').textContent = file.name;
        };
        reader.readAsText(file);
    }

    loadJSON(content) {
        try {
            const data = JSON.parse(content);
            this.schedule = this.parseJSONSchedule(data);
            this.render();
        } catch (e) {
            alert('Error parsing JSON: ' + e.message);
        }
    }

    loadCSV(content) {
        try {
            const lines = content.trim().split('\n');
            if (lines.length < 2) throw new Error('CSV must have header and data rows');

            const headers = lines[0].split(',').map(h => h.trim());
            const schedule = [];

            for (let i = 1; i < lines.length; i++) {
                const values = lines[i].split(',').map(v => v.trim());
                if (values.length !== headers.length) continue;

                const hourStr = values[0];
                const totalAgents = parseInt(values[1]) || 0;
                const breakdown = {};

                for (let j = 2; j < headers.length; j++) {
                    const customer = headers[j];
                    const agents = parseInt(values[j]) || 0;
                    if (agents > 0) {
                        breakdown[customer] = agents;
                    }
                }

                schedule.push({
                    hour: parseInt(hourStr) || (schedule.length),
                    total_agents: totalAgents,
                    breakdown: breakdown
                });
            }

            this.schedule = schedule;
            this.render();
        } catch (e) {
            alert('Error parsing CSV: ' + e.message);
        }
    }

    parseJSONSchedule(data) {
        // Handle array of objects format
        if (Array.isArray(data)) {
            return data.map(item => ({
                hour: item.hour || 0,
                total_agents: item.total_agents || 0,
                breakdown: item.breakdown || {}
            }));
        }
        throw new Error('Invalid JSON format');
    }

    getColorIntensity(agents, max) {
        if (max === 0) return 'low';
        const ratio = agents / max;
        if (ratio < 0.33) return 'low';
        if (ratio < 0.67) return 'medium';
        return 'high';
    }

    calculateStats() {
        if (!this.schedule || this.schedule.length === 0) {
            return {
                maxAgents: 0,
                avgAgents: 0,
                numCustomers: 0,
                peakHour: '-'
            };
        }

        const agents = this.schedule.map(s => s.total_agents);
        const maxAgents = Math.max(...agents);
        const avgAgents = Math.round(agents.reduce((a, b) => a + b, 0) / agents.length);

        const allCustomers = new Set();
        this.schedule.forEach(slot => {
            Object.keys(slot.breakdown).forEach(customer => allCustomers.add(customer));
        });

        const peakHourIndex = this.schedule.findIndex(s => s.total_agents === maxAgents);
        const peakHour = peakHourIndex !== -1 ? `${String(peakHourIndex).padStart(2, '0')}:00` : '-';

        return {
            maxAgents,
            avgAgents,
            numCustomers: allCustomers.size,
            peakHour
        };
    }

    render() {
        if (!this.schedule) return;

        const gridContainer = document.getElementById('gridContainer');
        gridContainer.innerHTML = '';

        const stats = this.calculateStats();

        // Update stats display
        document.getElementById('totalAgents').textContent = stats.maxAgents;
        document.getElementById('avgAgents').textContent = stats.avgAgents;
        document.getElementById('numCustomers').textContent = stats.numCustomers;
        document.getElementById('peakHour').textContent = stats.peakHour;

        // Render grid
        this.schedule.forEach((slot, index) => {
            const cell = document.createElement('div');
            cell.className = `hour-cell ${this.getColorIntensity(slot.total_agents, stats.maxAgents)}`;

            const hourStr = String(index).padStart(2, '0');
            const breakdownCount = Object.keys(slot.breakdown).length;

            cell.innerHTML = `
                <div>
                    <div class="hour-time">${hourStr}:00</div>
                    <div class="hour-agents">${slot.total_agents}</div>
                    <div class="hour-label">${breakdownCount} customer${breakdownCount !== 1 ? 's' : ''}</div>
                </div>
                <div class="tooltip">Click for details</div>
            `;

            cell.addEventListener('click', () => this.showModal(slot, hourStr));
            gridContainer.appendChild(cell);
        });
    }

    showModal(slot, hourStr) {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const breakdownList = document.getElementById('breakdownList');
        const modalTotal = document.getElementById('modalTotal');

        modalTitle.textContent = `Hour ${hourStr}:00 - Agent Breakdown`;

        breakdownList.innerHTML = '';
        if (Object.keys(slot.breakdown).length === 0) {
            breakdownList.innerHTML = '<li style="color: #999; padding: 12px 0;">No agents scheduled</li>';
        } else {
            Object.entries(slot.breakdown)
                .sort((a, b) => b[1] - a[1]) // Sort by agent count descending
                .forEach(([customer, agents]) => {
                    const li = document.createElement('li');
                    li.className = 'breakdown-item';
                    li.innerHTML = `
                        <span class="breakdown-customer">${customer}</span>
                        <span class="breakdown-agents">${agents}</span>
                    `;
                    breakdownList.appendChild(li);
                });
        }

        modalTotal.textContent = slot.total_agents;
        modal.style.display = 'block';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new SchedulerVisualizer();
});
