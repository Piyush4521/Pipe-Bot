import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { LandingNavbar } from '@/pages/landing/components/LandingNavbar';
import { LandingFooter } from '@/pages/landing/components/LandingFooter';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  AlertTriangle,
  ArrowLeft,
  ShieldAlert,
  Sliders,
  CheckCircle2,
  FileWarning,
  Activity,
  Layers,
} from 'lucide-react';

export const TermsPage: FC = () => {
  useDocumentTitle('Terms of Use (Draft)');

  return (
    <div className="min-h-screen flex flex-col bg-industrial-50 text-industrial-900 selection:bg-brand-orange selection:text-white">
      <LandingNavbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16">
        {/* Breadcrumb / Back Link */}
        <div className="mb-6">
          <NavLink
            to={ROUTES.HOME}
            className="inline-flex items-center gap-1.5 text-xs font-mono font-medium text-industrial-600 hover:text-brand-orange transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to System Home</span>
          </NavLink>
        </div>

        {/* Header Block */}
        <header className="space-y-4 mb-10 pb-6 border-b border-industrial-200">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" isMono className="bg-industrial-100 text-industrial-800">
              Terms & Conditions Draft
            </Badge>
            <Badge variant="brand" isMono>
              Prototype Advisory
            </Badge>
            <span className="text-xs font-mono text-industrial-500">
              Version 0.1.0-draft | Last Revised: October 2026
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-industrial-950">
            Terms of Use & Prototype Disclaimers
          </h1>

          <p className="text-base text-industrial-600 leading-relaxed">
            Essential operational limitations, safety boundaries, artificial intelligence verification requirements, and legal disclaimers governing the use of the PipeBot inspection platform.
          </p>
        </header>

        {/* Prominent Safety Warning Banner */}
        <Card variant="default" className="p-4 sm:p-5 mb-10 bg-red-50 border-red-300">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs text-red-950">
              <h2 className="font-bold uppercase tracking-wider font-mono text-red-950">
                Critical Safety Warning: Engineering Prototype Only
              </h2>
              <p className="leading-relaxed">
                PipeBot is an active engineering research platform and software prototype. It is NOT commercially certified, NOT field-certified under municipal standards, and NOT designed for autonomous safety-critical pipeline decisions. All automated detections and distance metrics must be verified by licensed civil infrastructure engineers.
              </p>
            </div>
          </div>
        </Card>

        {/* Content Body */}
        <article className="space-y-10 text-sm leading-relaxed text-industrial-700">
          {/* Section 1 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                1. Prototype Status & Non-Certified Nature
              </h2>
            </div>
            <p>
              The PipeBot software interface, hardware configurations, and sensor integrations are provided strictly for research, benchmarking, and controlled testing. No claim of compliance with international pipeline assessment standards (including NASSCO PACP, WRc MSCC, ASTM, or ISO standards) is made or implied.
            </p>
          </section>

          {/* Section 2 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                2. Hardware Actuation & Propulsion Interlocks
              </h2>
            </div>
            <p>
              In this frontend release:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                All vehicle propulsion controls, directional D-pads, motor speed sliders, and automated drive commands are genuinely disabled and locked via software interlocks.
              </li>
              <li>
                Emergency stop interfaces indicate intended system architectures but cannot command physical motor cutoff until embedded microcode and physical relay hardware are deployed.
              </li>
              <li>
                Operators must not attempt to connect unsupported high-voltage motor drivers or bypass frontend safety locks.
              </li>
            </ul>
          </section>

          {/* Section 3 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                3. Artificial Intelligence & YOLO Anomaly Detection
              </h2>
            </div>
            <p>
              The integrated defect detection engine evaluates pipeline imagery across four specific classes: <em>deformation</em>, <em>misalignment</em>, <em>obstacle</em>, and <em>rupture</em>.
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                <strong>Advisory Detections Only:</strong> Detections, bounding boxes, and classifications produced by the YOLO neural network are automated advisory alerts. They do not constitute an authoritative structural engineering assessment.
              </li>
              <li>
                <strong>Confidence Score Definition:</strong> Confidence values (e.g. 88% or 0.88) represent statistical model probability based on training weights. Confidence scores do NOT indicate physical defect severity, structural wall thickness loss, or remaining conduit lifespan.
              </li>
              <li>
                <strong>Mandatory Human-in-the-Loop Review:</strong> Every automated detection must be independently inspected, verified, or dismissed by an authorized pipeline inspection technician before issuing excavation or repair orders.
              </li>
            </ul>
          </section>

          {/* Section 4 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                4. Odometry & Spatial Distance Estimation Limitations
              </h2>
            </div>
            <p>
              Conduit penetration distance is estimated based on rotary optical wheel encoder pulses:
            </p>
            <div className="p-3 bg-industrial-100 border border-industrial-300 rounded-sm font-mono text-xs text-industrial-800">
              Circumference = PI * WheelDiameter<br />
              Distance = (EncoderPulses / PulsesPerRevolution) * Circumference
            </div>
            <p className="text-industrial-600">
              Operators are explicitly notified that estimated distance is subject to cumulative error caused by wheel slippage on wet or silted PVC surfaces, wheel diameter variations under load, vehicle trajectory yaw, and optical sensor resolution limits. Odometry figures must never be treated as certified land-surveying or geodetic coordinates.
            </p>
          </section>

          {/* Section 5 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <FileWarning className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                5. Inspection Reports & Safety-Critical Exclusions
              </h2>
            </div>
            <p>
              Automated inspection reports compiled by the platform are draft technical summaries. They must not be submitted as certified compliance documentation for insurance, municipal permit acquisition, or regulatory handover without stamp and signoff from a certified professional engineer.
            </p>
          </section>

          {/* Section 6 */}
          <section className="space-y-3 pt-4 border-t border-industrial-200">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-industrial-600" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                6. Legal Reservation & Review Note
              </h2>
            </div>
            <p className="text-xs text-industrial-500 font-mono">
              Notice: These Terms of Use are preliminary engineering guidelines. Complete terms, limitation of liability clauses, and commercial warranties must be drafted and approved by qualified legal counsel prior to commercial licensing.
            </p>
          </section>
        </article>

        {/* Footer Navigation */}
        <div className="mt-12 pt-6 border-t border-industrial-200 flex flex-wrap items-center justify-between gap-4">
          <NavLink to={ROUTES.PRIVACY}>
            <Button variant="outline" size="sm">
              View Privacy Policy Draft
            </Button>
          </NavLink>
          <NavLink to={ROUTES.DASHBOARD.ROOT}>
            <Button variant="primary" size="sm">
              Open Operator Console
            </Button>
          </NavLink>
        </div>
      </main>

      <LandingFooter />
    </div>
  );
};

