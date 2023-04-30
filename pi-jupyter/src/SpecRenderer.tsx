import * as React from 'react';
import { useEffect, useRef } from 'react';
import { PIWorkflow } from 'pi-client';
import GridLoader from 'react-spinners/GridLoader';
import { socket } from './PISocket';

interface ISpecRendererProps {
  session: string;
  spec?: unknown;
  visible: boolean;
}

export function SpecRenderer({ session, spec, visible }: ISpecRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && spec !== undefined) {
      const containerElement = containerRef.current;

      const workflow = PIWorkflow(socket, session, { enableHelp: false });

      // Spec changed, clear the container
      while (containerElement.firstChild) {
        containerElement.removeChild(containerElement.firstChild);
      }
      workflow.init(spec, containerRef.current);
    }
  }, [containerRef, spec]);

  return (
    <div
      className={
        visible ? 'jp-PI-SpecRenderer activeSpec' : 'jp-PI-SpecRenderer'
      }
    >
      {spec ? (
        <div className="jp-PI-RenderedSpecContainer" ref={containerRef}></div>
      ) : (
        <GridLoader color="#000000" loading={true} size={16} />
      )}
    </div>
  );
}
