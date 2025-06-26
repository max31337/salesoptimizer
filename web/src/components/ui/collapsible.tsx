"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface CollapsibleProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
  className?: string
}

const Collapsible = React.forwardRef<HTMLDivElement, CollapsibleProps>(
  ({ open = false, onOpenChange, children, className, ...props }, ref) => {
    const [isOpen, setIsOpen] = React.useState(open)
    
    React.useEffect(() => {
      setIsOpen(open)
    }, [open])
    
    const handleToggle = () => {
      const newState = !isOpen
      setIsOpen(newState)
      onOpenChange?.(newState)
    }
    
    return (
      <div 
        ref={ref} 
        className={cn(className)} 
        data-state={isOpen ? "open" : "closed"}
        {...props}
      >
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            if ((child as any).type === CollapsibleTrigger) {
              return React.cloneElement(child as any, { onClick: handleToggle })
            }
            if ((child as any).type === CollapsibleContent) {
              return React.cloneElement(child as any, { isOpen })
            }
          }
          return child
        })}
      </div>
    )
  }
)
Collapsible.displayName = "Collapsible"

interface CollapsibleTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
}

const CollapsibleTrigger = React.forwardRef<HTMLButtonElement, CollapsibleTriggerProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn("w-full", className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)
CollapsibleTrigger.displayName = "CollapsibleTrigger"

interface CollapsibleContentProps {
  children: React.ReactNode
  isOpen?: boolean
  className?: string
}

const CollapsibleContent = React.forwardRef<HTMLDivElement, CollapsibleContentProps>(
  ({ children, isOpen = false, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "overflow-hidden transition-all duration-200 ease-in-out",
          isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0",
          className
        )}
        data-state={isOpen ? "open" : "closed"}
        {...props}
      >
        <div className="pb-1">
          {children}
        </div>
      </div>
    )
  }
)
CollapsibleContent.displayName = "CollapsibleContent"

export { Collapsible, CollapsibleTrigger, CollapsibleContent }
