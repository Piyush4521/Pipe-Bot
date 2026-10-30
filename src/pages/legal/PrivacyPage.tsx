import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';
import { LandingNavbar } from '@/pages/landing/components/LandingNavbar';
import { LandingFooter } from '@/pages/landing/components/LandingFooter';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Shield, AlertTriangle, ArrowLeft, FileText, Database, Lock, Clock, Info } from 'lucide-react';

export const PrivacyPage: FC = () => {
  useDocumentTitle('Privacy Policy (Draft)');

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
              Governance Draft
            </Badge>
            <Badge variant="brand" isMono>
              Internal Engineering Review
            </Badge>
            <span className="text-xs font-mono text-industrial-500">
              Version 0.1.0-draft | Last Revised: October 2026
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-industrial-950">
            Privacy Policy & Data Architecture Draft
          </h1>

          <p className="text-base text-industrial-600 leading-relaxed">
            Technical and operational disclosure regarding data categories, telemetry processing, local storage architecture, and data governance for the PipeBot inspection platform.
          </p>
        </header>

        {/* Prominent Legal Disclaimer Banner */}
        <Card variant="default" className="p-4 sm:p-5 mb-10 bg-amber-50 border-amber-300">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs text-amber-900">
              <h2 className="font-bold uppercase tracking-wider text-amber-950 font-mono">
                Notice: Engineering Prototype Draft
              </h2>
              <p className="leading-relaxed">
                This document is an engineering draft prepared exclusively for prototype architecture evaluation. It does not constitute binding legal counsel, a commercial service privacy commitment, or a finalized institutional policy. Formal legal, municipal compliance, and regulatory review must be conducted prior to any commercial deployment.
              </p>
            </div>
          </div>
        </Card>

        {/* Content Body */}
        <article className="space-y-10 text-sm leading-relaxed text-industrial-700">
          {/* Section 1 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                1. Scope & Categories of Information Processed
              </h2>
            </div>
            <p>
              The PipeBot robotic platform is designed for industrial conduit evaluation. In its current implementation, the system does not collect personal user profiles, tracking cookies, advertising identifiers, or consumer behavioral data. The system is architected to process the following technical and operational categories:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                <strong className="text-industrial-900">Inspection Session Metadata:</strong> Conduit identifier, nominal diameter (mm), material classification (rigid PVC), operator workstation ID, session start time, and completion timestamp.
              </li>
              <li>
                <strong className="text-industrial-900">Defect Detection Records:</strong> Neural network anomaly classifications (deformation, misalignment, obstacle, rupture), bounding box spatial coordinates, model confidence scores, and engineer review statuses.
              </li>
              <li>
                <strong className="text-industrial-900">Pipeline Imagery & Video:</strong> Optical image frames captured by the onboard OV2640 camera sensor inside pipe conduits, associated with optical frame identifiers.
              </li>
              <li>
                <strong className="text-industrial-900">Vehicle & Odometry Telemetry:</strong> Rotary encoder pulse counts, wheel RPM, estimated conduit penetration depth (meters), 6-axis IMU acceleration, pitch gradient (slope), roll, battery voltage, and motor driver state.
              </li>
              <li>
                <strong className="text-industrial-900">System Configuration:</strong> Local network endpoint parameters, WebSocket connection addresses, and operator application mode settings.
              </li>
            </ul>
          </section>

          {/* Section 2 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                2. Processing Architecture & Local Ingestion
              </h2>
            </div>
            <p>
              PipeBot operates under an edge-first, decoupled local processing topology:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                <strong>Local Network Transport:</strong> Video frames and odometry telemetry are transmitted over a private, local 2.4 GHz Wi-Fi link directly from the onboard microcontrollers (ESP32-CAM and ESP32-WROOM-32) to the operator workstation.
              </li>
              <li>
                <strong>No Public Cloud Routing:</strong> Pipeline video streams, raw image frames, and telemetry are not routed through public cloud databases, third-party CDNs, or external artificial intelligence cloud APIs.
              </li>
              <li>
                <strong>On-Premise Inference:</strong> YOLO neural network defect detection runs locally on the edge processing computer equipped with OpenCV and Python runtime environments.
              </li>
            </ul>
          </section>

          {/* Section 3 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                3. Future Backend & Cloud Storage Provisions
              </h2>
            </div>
            <p>
              In subsequent production stages (post-frontend prototype), the platform roadmap includes:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                <strong>Local Relational Database:</strong> Storage of mission history and defect records in a secure local PostgreSQL or SQLite instance managed by the FastAPI backend service.
              </li>
              <li>
                <strong>Optional Enterprise Cloud Synchronization:</strong> If enterprise operators deliberately configure remote synchronization, archived compliance inspection reports and aggregated condition audits may be uploaded to customer-managed cloud buckets with mutual TLS encryption.
              </li>
            </ul>
          </section>

          {/* Section 4 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                4. Data Retention & Policy Review
              </h2>
            </div>
            <p>
              Because PipeBot is currently a development prototype:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-industrial-600">
              <li>
                Data retention schedules for raw video archives, encoder logs, and detection histories must be defined by municipal infrastructure authorities or pipeline operating contractors in accordance with regional infrastructure retention statutes.
              </li>
              <li>
                In the current frontend development release, Disconnected Mode holds no persisted historical data, and Demo Mode stores simulation objects strictly in volatile browser memory.
              </li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-orange" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                5. Security Considerations & Unresolved Items
              </h2>
            </div>
            <p>
              The following technical security and governance items are designated for formal review prior to commercial field release:
            </p>
            <div className="p-4 bg-industrial-100 border border-industrial-300 rounded-sm font-mono text-xs space-y-1.5 text-industrial-800">
              <div>[ ] Implementation of mTLS authentication on ESP32 local Wi-Fi links</div>
              <div>[ ] Hardened JWT role-based access control (RBAC) on backend REST endpoints</div>
              <div>[ ] Formal data processing agreement (DPA) templates for municipal contractors</div>
              <div>[ ] Cryptographic SHA-256 integrity hashing for exported compliance reports</div>
            </div>
          </section>

          {/* Section 6 */}
          <section className="space-y-3 pt-4 border-t border-industrial-200">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-industrial-600" />
              <h2 className="text-lg font-bold text-industrial-950 font-mono uppercase tracking-tight">
                6. Contact Placeholder
              </h2>
            </div>
            <p className="text-xs text-industrial-500 font-mono">
              Project Inquiries: [PipeBot Engineering Team Lead / Project Maintainer Placeholder]<br />
              Repository: github.com/Piyush4521/Pipe-Bot (Academic & Development Project)
            </p>
          </section>
        </article>

        {/* Footer Navigation */}
        <div className="mt-12 pt-6 border-t border-industrial-200 flex flex-wrap items-center justify-between gap-4">
          <NavLink to={ROUTES.TERMS}>
            <Button variant="outline" size="sm">
              View Terms of Use Draft
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

