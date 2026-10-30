import type { FC } from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Radio } from 'lucide-react';

export const ArchitectureSection: FC = () => {
  return (
    <section id="architecture" className="py-16 lg:py-24 bg-industrial-50 border-b border-industrial-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 pb-5 border-b border-industrial-200 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-brand-orange">
                03 // Technical Topology
              </span>
              <Badge variant="outline" isMono>Decoupled Dual-MCU Architecture</Badge>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-industrial-950">
              System Architecture & Communication Flow
            </h2>
            <p className="text-sm text-industrial-600 max-w-2xl leading-relaxed">
              Decoupling camera streaming from motor control eliminates timing jitter, ensuring responsive locomotion and high-throughput video ingestion.
            </p>
          </div>

          <div className="text-xs font-mono text-industrial-500 uppercase tracking-wider">
            Topology: Dual Hardware Transmitters → Edge Processing Server
          </div>
        </div>

        {/* Master Architecture Diagram Card */}
        <Card variant="raised" className="overflow-hidden border-industrial-300">
          <div className="px-5 py-3 bg-industrial-900 text-white flex flex-wrap items-center justify-between text-xs font-mono border-b border-industrial-900 gap-2">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-brand-orange animate-pulse" />
              <span className="font-bold uppercase tracking-wider">Fig 2.0 | End-to-End System Architecture Topology</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-industrial-400">Wireless: Local 2.4 GHz Wi-Fi</span>
              <Badge variant="outline" isMono className="bg-industrial-800 text-white border-industrial-700 text-[10px]">
                No Cloud Latency
              </Badge>
            </div>
          </div>

          {/* Responsive SVG Architecture Map */}
          <div className="p-4 sm:p-6 bg-white overflow-x-auto">
            <div className="min-w-[760px]">
              <svg
                viewBox="0 0 960 540"
                className="w-full h-auto select-none font-mono"
                xmlns="http://www.w3.org/2000/svg"
                role="img"
                aria-label="Technical architecture diagram showing separate ESP32-CAM and ESP32-WROOM-32 controllers streaming over local Wi-Fi to a Python FastAPI processing server with YOLO inference and web dashboard"
              >
                {/* Background Grid Lines */}
                <defs>
                  <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#0F172A" />
                  </marker>
                  <marker id="arrowheadOrange" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#EA580C" />
                  </marker>
                  <marker id="arrowheadGreen" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#16A34A" />
                  </marker>
                </defs>

                {/* ZONE 1: ROBOTIC CRAWLER (HARDWARE PLATFORM) */}
                <rect x="20" y="30" width="280" height="480" rx="4" fill="#F8F9FA" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="4,4" />
                <rect x="20" y="30" width="280" height="26" rx="4" fill="#E2E8F0" />
                <text x="32" y="47" fill="#0F172A" fontSize="11" fontWeight="700">
                  ROBOTIC CRAWLER PLATFORM (ONBOARD)
                </text>

                {/* Subsystem A: ESP32-CAM (Imaging Only) */}
                <rect x="36" y="70" width="248" height="150" rx="3" fill="#FFFFFF" stroke="#EA580C" strokeWidth="2" />
                <rect x="36" y="70" width="248" height="24" rx="3" fill="#EA580C" />
                <text x="44" y="86" fill="#FFFFFF" fontSize="10" fontWeight="700">
                  DEVICE 1: AI THINKER ESP32-CAM
                </text>
                <text x="46" y="112" fill="#0F172A" fontSize="9" fontWeight="600">• OV2640 2MP Image Sensor</text>
                <text x="46" y="130" fill="#475569" fontSize="8.5">• High-Output Forward LED Ring</text>
                <text x="46" y="148" fill="#475569" fontSize="8.5">• Microcontroller Internal PSRAM Buffer</text>
                <text x="46" y="166" fill="#475569" fontSize="8.5">• JPEG Frame Compression</text>
                <rect x="46" y="180" width="228" height="24" fill="#FFF7ED" stroke="#FDBA74" strokeWidth="1" />
                <text x="54" y="196" fill="#EA580C" fontSize="8.5" fontWeight="700">Output: Wi-Fi MJPEG Video Stream</text>

                {/* Subsystem B: ESP32-WROOM-32 (Motion & Telemetry) */}
                <rect x="36" y="245" width="248" height="245" rx="3" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2" />
                <rect x="36" y="245" width="248" height="24" rx="3" fill="#0F172A" />
                <text x="44" y="261" fill="#FFFFFF" fontSize="10" fontWeight="700">
                  DEVICE 2: ESP32-WROOM-32 (CORE)
                </text>
                <text x="46" y="287" fill="#0F172A" fontSize="9" fontWeight="600">• L298N Dual H-Bridge Motor Driver</text>
                <text x="46" y="305" fill="#475569" fontSize="8.5">• 4x DC Geared Motors (4WD Locomotion)</text>
                <text x="46" y="323" fill="#475569" fontSize="8.5">• Left Wheel Optical Encoder (Interrupt pin)</text>
                <text x="46" y="341" fill="#475569" fontSize="8.5">• Right Wheel Optical Encoder (Interrupt pin)</text>
                <text x="46" y="359" fill="#475569" fontSize="8.5">• MPU6050 6-Axis IMU (I2C Pitch/Roll)</text>
                <text x="46" y="377" fill="#475569" fontSize="8.5">• Battery Voltage Divider ADC Circuit</text>
                <rect x="46" y="445" width="228" height="28" fill="#F1F3F5" stroke="#CBD5E1" strokeWidth="1" />
                <text x="54" y="462" fill="#0F172A" fontSize="8.5" fontWeight="700">Output: Wi-Fi JSON Telemetry Packets</text>

                {/* WIRELESS TRANSMISSION CHANNEL */}
                {/* Video Stream Line */}
                <path d="M 284 145 L 375 145" stroke="#EA580C" strokeWidth="2.5" markerEnd="url(#arrowheadOrange)" />
                <text x="295" y="137" fill="#EA580C" fontSize="8.5" fontWeight="700">Wi-Fi Stream</text>

                {/* Telemetry Stream Line */}
                <path d="M 284 455 L 375 455" stroke="#0F172A" strokeWidth="2.5" markerEnd="url(#arrowhead)" />
                <text x="295" y="447" fill="#0F172A" fontSize="8.5" fontWeight="700">Wi-Fi Telemetry</text>

                {/* ZONE 2: LOCAL PROCESSING SERVER (PYTHON / FASTAPI / YOLO) */}
                <rect x="380" y="30" width="310" height="480" rx="4" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2" />
                <rect x="380" y="30" width="310" height="26" rx="4" fill="#0F172A" />
                <text x="392" y="47" fill="#FFFFFF" fontSize="11" fontWeight="700">
                  LOCAL PROCESSING SERVER (PYTHON 3.11)
                </text>

                {/* Processing Submodules */}
                {/* 1. Frame Ingestion & OpenCV */}
                <rect x="396" y="75" width="278" height="60" rx="2" fill="#F8F9FA" stroke="#CBD5E1" strokeWidth="1" />
                <text x="406" y="93" fill="#0F172A" fontSize="9.5" fontWeight="700">1. Frame Ingestion Layer (OpenCV)</text>
                <text x="406" y="110" fill="#64748B" fontSize="8.5">• MJPEG Frame Decoding & Resizing</text>
                <text x="406" y="124" fill="#64748B" fontSize="8.5">• Frame ID Indexing & Timestamp Generation</text>

                {/* Internal Pipeline Arrow */}
                <line x1="535" y1="135" x2="535" y2="160" stroke="#EA580C" strokeWidth="2" markerEnd="url(#arrowheadOrange)" />

                {/* 2. YOLO Neural Inference */}
                <rect x="396" y="165" width="278" height="90" rx="2" fill="#FFF7ED" stroke="#EA580C" strokeWidth="2" />
                <text x="406" y="185" fill="#EA580C" fontSize="10" fontWeight="700">2. YOLO Anomaly Detection Engine</text>
                <text x="406" y="202" fill="#475569" fontSize="8.5">• PyTorch Convolutional Pipeline</text>
                <text x="406" y="217" fill="#475569" fontSize="8.5">• Classes: Deformation, Misalignment, Obstacle, Rupture</text>
                <text x="406" y="232" fill="#475569" fontSize="8.5">• Output: Bounding Boxes + Confidence Scores</text>
                <text x="406" y="247" fill="#C2410C" fontSize="8" fontWeight="600">※ Inference executes on server, NOT on ESP32</text>

                {/* Internal Pipeline Arrow */}
                <line x1="535" y1="255" x2="535" y2="280" stroke="#0F172A" strokeWidth="2" markerEnd="url(#arrowhead)" />

                {/* 3. Spatial Localization & Odometry Fusion */}
                <rect x="396" y="285" width="278" height="90" rx="2" fill="#F8F9FA" stroke="#CBD5E1" strokeWidth="1" />
                <text x="406" y="305" fill="#0F172A" fontSize="9.5" fontWeight="700">3. Spatial Localization & Odometry Fusion</text>
                <text x="406" y="322" fill="#64748B" fontSize="8.5">• Accumulate Left/Right Encoder Pulses</text>
                <text x="406" y="337" fill="#64748B" fontSize="8.5">• Calculate Estimated Distance: D = (Ticks / PPR) * πD</text>
                <text x="406" y="352" fill="#64748B" fontSize="8.5">• Synchronize Frame ID with Spatial Meter Marker</text>
                <text x="406" y="367" fill="#64748B" fontSize="8.5">• Calibrate Slip Tolerances & IMU Pitch Corrections</text>

                {/* Internal Pipeline Arrow */}
                <line x1="535" y1="375" x2="535" y2="400" stroke="#0F172A" strokeWidth="2" markerEnd="url(#arrowhead)" />

                {/* 4. Telemetry Aggregator & FastAPI WebSockets */}
                <rect x="396" y="405" width="278" height="85" rx="2" fill="#F0FDF4" stroke="#16A34A" strokeWidth="1.5" />
                <text x="406" y="425" fill="#16A34A" fontSize="9.5" fontWeight="700">4. FastAPI Backend & WebSocket Hub</text>
                <text x="406" y="442" fill="#334155" fontSize="8.5">• Asynchronous WebSocket Telemetry Stream</text>
                <text x="406" y="457" fill="#334155" fontSize="8.5">• Annotated Frame Dispatcher</text>
                <text x="406" y="472" fill="#334155" fontSize="8.5">• REST Endpoints for History & Reporting</text>

                {/* Output Lines from Server to Database and Web App */}
                <path d="M 690 445 L 750 445" stroke="#16A34A" strokeWidth="2.5" markerEnd="url(#arrowheadGreen)" />
                <text x="696" y="437" fill="#16A34A" fontSize="8" fontWeight="700">WebSockets</text>

                <path d="M 690 330 L 750 330" stroke="#0F172A" strokeWidth="2" markerEnd="url(#arrowhead)" />
                <text x="700" y="322" fill="#0F172A" fontSize="8" fontWeight="700">SQL Write</text>

                {/* ZONE 3: STORAGE & USER INTERFACE */}
                {/* Database Block */}
                <rect x="755" y="280" width="185" height="100" rx="3" fill="#FFFFFF" stroke="#0F172A" strokeWidth="1.5" />
                <rect x="755" y="280" width="185" height="24" rx="3" fill="#1E293B" />
                <text x="765" y="296" fill="#FFFFFF" fontSize="9.5" fontWeight="700">
                  PERSISTENCE (SQLITE)
                </text>
                <text x="765" y="320" fill="#475569" fontSize="8.5">• Inspection Missions</text>
                <text x="765" y="336" fill="#475569" fontSize="8.5">• Defect Event Logs</text>
                <text x="765" y="352" fill="#475569" fontSize="8.5">• Odometry Time-Series</text>
                <text x="765" y="368" fill="#475569" fontSize="8.5">• Defect Snapshot Files</text>

                {/* Operator Web Dashboard */}
                <rect x="755" y="400" width="185" height="110" rx="3" fill="#FFFFFF" stroke="#EA580C" strokeWidth="2" />
                <rect x="755" y="400" width="185" height="24" rx="3" fill="#EA580C" />
                <text x="765" y="416" fill="#FFFFFF" fontSize="9.5" fontWeight="700">
                  WEB OPERATOR DASHBOARD
                </text>
                <text x="765" y="440" fill="#0F172A" fontSize="8.5" fontWeight="600">• React + Vite + TypeScript</text>
                <text x="765" y="456" fill="#475569" fontSize="8.5">• Live Video & Bounding Boxes</text>
                <text x="765" y="472" fill="#475569" fontSize="8.5">• Real-Time Distance & Odometry</text>
                <text x="765" y="488" fill="#475569" fontSize="8.5">• Automated PDF Reports</text>
              </svg>
            </div>
          </div>

          {/* Architecture Architectural Highlights Footer */}
          <div className="p-4 bg-industrial-100 border-t border-industrial-200 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div>
              <span className="font-bold text-industrial-900 block mb-0.5">Physical Controller Isolation</span>
              <p className="text-industrial-600">
                ESP32-CAM and ESP32-WROOM-32 operate on independent power buses and firmware loops, isolating motor noise from optical sensors.
              </p>
            </div>
            <div>
              <span className="font-bold text-industrial-900 block mb-0.5">Server-Side Inference</span>
              <p className="text-industrial-600">
                Ultralytics YOLO runs exclusively on the host workstation. Microcontrollers handle low-level I/O and frame transmission only.
              </p>
            </div>
            <div>
              <span className="font-bold text-industrial-900 block mb-0.5">Local Network Operation</span>
              <p className="text-industrial-600">
                Zero dependence on cloud pipelines. Raw video is decoded locally and never routed through cloud databases or remote storage.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
};
