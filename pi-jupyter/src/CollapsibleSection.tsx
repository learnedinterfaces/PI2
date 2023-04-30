import * as React from 'react';

interface ICollapsibleSectionProps {
  title: string;
  defaultCollapsed?: boolean;
}

export function CollapsibleSection({
  title,
  defaultCollapsed = true,
  children
}: React.PropsWithChildren<ICollapsibleSectionProps>) {
  const [collapsed, setCollapsed] = React.useState(defaultCollapsed);
  return (
    <div className="jp-PI-Collapsible">
      <button
        className="jp-PI-CollapseButton"
        onClick={() => setCollapsed(!collapsed)}
      >
        {title}
      </button>
      {!collapsed && children}
    </div>
  );
}
